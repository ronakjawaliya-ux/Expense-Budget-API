from flask import Flask, request
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from datetime import datetime
import sqlite3
import hashlib
import os
import secrets


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", secrets.token_urlsafe(32))
jwt = JWTManager(app)

DATABASE = "expense_budget.db"

def connect_database():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_table():
    conn = connect_database()
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS expenses (
                        transaction_id INTEGER PRIMARY KEY,
                        amount REAL ,
                        category TEXT ,
                        date TEXT,
                        user_id INTEGER NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                        )
                """)

    cur.execute("""CREATE TABLE IF NOT EXISTS budget (
                        budget_id INTEGER PRIMARY KEY,
                        amount REAL,
                        user_id INTEGER NOT NULL UNIQUE,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                        )
                """)

    cur.execute("""CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE,
                        password_hash TEXT
                        )
                """)

    # Support databases created before user-specific expenses and budgets.
    expense_columns = [column[1] for column in cur.execute("PRAGMA table_info(expenses)")]
    if "user_id" not in expense_columns:
        cur.execute("ALTER TABLE expenses ADD COLUMN user_id INTEGER REFERENCES users(user_id)")

    budget_columns = [column[1] for column in cur.execute("PRAGMA table_info(budget)")]
    if "user_id" not in budget_columns:
        cur.execute("ALTER TABLE budget ADD COLUMN user_id INTEGER REFERENCES users(user_id)")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_budget_user_id ON budget(user_id)")

    conn.commit()
    conn.close()


def current_user_id():
    return int(get_jwt_identity())



@app.route('/')
def home():
    return "Expense Budget API is running!"



@app.route('/register', methods=['POST'])
def register():


    data = request.get_json()


    if "username" not in data or "password" not in data:
        return {"message": "Missing required fields."}, 400

    password_hash = hashlib.sha256(data["password"].encode()).hexdigest()


    conn = connect_database()
    cur = conn.cursor()

    try:
        cur.execute("""
                INSERT INTO users (username, password_hash)
                VALUES (?, ?)
        """,(data["username"], password_hash))

        conn.commit()

    except sqlite3.IntegrityError:
        conn.close()
        return {"message": "Username already exists."}, 409

    conn.close()

    return {"message": "User registered successfully!"}



@app.route('/login', methods=['POST'])
def login():


    data = request.get_json()


    if "username" not in data or "password" not in data:
        return {"message": "Missing required fields."}, 400


    password_hash = hashlib.sha256(data["password"].encode()).hexdigest()


    conn = connect_database()
    cur = conn.cursor()


    cur.execute("""
        SELECT * FROM users
        WHERE username = ? AND password_hash = ?
    """, (data["username"], password_hash))


    row = cur.fetchone()


    if row is None:
       conn.close()
       return {"message": "Invalid username or password."}, 401


    user_id = row[0]
    conn.close()
    access_token = create_access_token(identity=str(user_id))
    return {"message": "Login successful!", "access_token": access_token}



@app.route('/expenses', methods=['POST'])
@jwt_required()
def add_expense():

    data = request.get_json()

    if "amount" not in data or "category" not in data or "date" not in data:
        return {"message": "Missing required fields."}, 400

    if not isinstance(data["amount"], int) and not isinstance(data["amount"], float):
        return {"message": "Amount must be a number."}, 400

    if not isinstance(data["category"], str):
        return {"message": "Category must be a string."}, 400

    try:
        datetime.strptime(data["date"], "%Y-%m-%d")
    except ValueError:
        return {"message": "Date must be in YYYY-MM-DD format."}, 400

    conn = connect_database()
    cur = conn.cursor()
    user_id = current_user_id()
    
    cur.execute("""INSERT INTO expenses (amount, category, date, user_id)
                VALUES (?, ?, ?, ?)""",
                (data["amount"], data["category"], data["date"], user_id)
                )
    
    conn.commit()
    transaction_id = cur.lastrowid
    data["transaction_id"] = transaction_id
    conn.close()
    return data



@app.route('/budget', methods=['POST'])
@jwt_required()
def set_budget():
    
    data = request.get_json()
    
    if "amount" not in data:
        return {"message": "Missing required field."}, 400

    if not isinstance(data["amount"], int) and not isinstance(data["amount"], float):
        return {"message": "Amount must be a number."}, 400
    
    conn = connect_database()
    cur = conn.cursor()
    user_id = current_user_id()
    
    cur.execute("SELECT * FROM budget WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    
    if row is None:
        cur.execute("""
            INSERT INTO budget (amount, user_id)
            VALUES (?, ?)
        """,(data["amount"], user_id))
    else:
        cur.execute("""
            UPDATE budget
            SET amount = ?
            WHERE budget_id = ? AND user_id = ?
        """, (data["amount"], row[0], user_id))
    
    conn.commit()
    conn.close()
    
    return {"message": "Budget set successfully!"}



@app.route('/expenses', methods=['GET'])
@jwt_required()
def get_expenses():
    
    category = request.args.get("category")
    date = request.args.get("date")
    
    if date:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {"message": "Date must be in YYYY-MM-DD format."}, 400
        
    min_amount = request.args.get("min_amount")
    max_amount = request.args.get("max_amount")
    
    if min_amount:
        try:
            min_amount = float(min_amount)
        except ValueError:
            return {"message": "min_amount must be a number."}, 400
    
    if max_amount:
        try:
            max_amount = float(max_amount)
        except ValueError:
            return {"message": "max_amount must be a number."}, 400
    
    if min_amount is not None and max_amount is not None:
        if min_amount > max_amount:
            return {"message": "min_amount cannot be greater than max_amount."}, 400
    
    conn = connect_database()
    cur = conn.cursor()
    user_id = current_user_id()
    
    query = "SELECT * FROM expenses WHERE user_id = ?"
    params = [user_id]
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    if date:
        query += " AND date = ?"
        params.append(date)
    
    if min_amount is not None:
        query += " AND amount >= ?"
        params.append(min_amount)
    
    if max_amount is not None:
        query += " AND amount <= ?"
        params.append(max_amount)
    
    cur.execute(query, params)
    
    rows = cur.fetchall()
    expense_data = []
    for row in rows:
        expense = {
            "transaction_id": row[0],
            "amount": row[1],
            "category": row[2],
            "date": row[3]
        }
        expense_data.append(expense)
    
    conn.close()
    return expense_data



@app.route('/expenses/statistics', methods=['GET'])
@jwt_required()
def expense_statistics():
    conn = connect_database()
    cur = conn.cursor()
    user_id = current_user_id()
    cur.execute("""SELECT COUNT(*), SUM(amount), AVG(amount), MAX(amount), MIN(amount)
                FROM expenses WHERE user_id = ?""", (user_id,))
    
    row = cur.fetchone()
    conn.close()
    
    return {"total_expenses": row[0],
            "total_amount": row[1],
            "average_amount": row[2],
            "highest_amount": row[3],
            "lowest_amount": row[4]
    }



@app.route('/expenses/category-summary', methods=['GET'])
@jwt_required()
def category_summary():
    conn = connect_database()
    cur = conn.cursor()
    user_id = current_user_id()

    cur.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()

    category_data = {}

    for row in rows:
        category_data[row[0]] = row[1]

    return category_data



@app.route('/budget', methods=['GET'])
@jwt_required()
def get_budget():

    conn = connect_database()
    cur = conn.cursor()
    user_id = current_user_id()

    cur.execute("""SELECT * FROM budget WHERE user_id = ?""", (user_id,))
    row = cur.fetchone()

    if row is None:
        conn.close()
        return {"message": "Budget not found."}, 404

    budget = {
        "budget_id": row[0],
        "amount": row[1],
    }

    conn.close()
    return budget



@app.route('/budget/alert', methods=['GET'])
@jwt_required()
def budget_alert():
    
    conn = connect_database()
    cur = conn.cursor()
    user_id = current_user_id()
    
    cur.execute("""
                SELECT amount 
                FROM budget
                WHERE user_id = ?
    """, (user_id,))
    
    row = cur.fetchone()
    
    
    if row is None:
        conn.close()
        return {"message": "Budget not found."}, 404
    
    
    budget = row[0]
    
    
    cur.execute("""
                SELECT SUM(amount)
                FROM expenses
                WHERE user_id = ?
    """, (user_id,))
    
    expense_row = cur.fetchone()
    
    
    if expense_row[0] is None:
        spent = 0
    else:
        spent = expense_row[0]
    
    
    percentage_used = round((spent / budget) * 100, 2)
    
    
    if percentage_used < 80:
        message = "Budget is under control."
    elif percentage_used < 100:
        message = "Warning: You are approaching your budget."
    else:
        message = "Alert: You have exceeded your budget."


    conn.close()
    
    return {
        "budget": budget,
        "spent": spent,
        "percentage_used": percentage_used,
        "message": message
    }
    
    
    
@app.route('/expenses/<transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(transaction_id):

    try:
        transaction_id = int(transaction_id)
    except ValueError:
        return {"message": "Transaction id must be an integer."}, 400
    
    conn = connect_database()
    cur = conn.cursor()
    user_id = current_user_id()
    cur.execute(
    """SELECT * FROM expenses WHERE transaction_id = ? AND user_id = ?""", (transaction_id, user_id))
    
    row = cur.fetchone()
    
    if row is None:
        conn.close()
        return {"message": "Expense not found."}, 404
    
    cur.execute(
    """DELETE FROM expenses WHERE transaction_id = ? AND user_id = ?""", (transaction_id, user_id))

    conn.commit()
    conn.close()
    
    return{"message": "Expense deleted successfully!"}



@app.route('/expenses/<transaction_id>', methods=['PUT'])
@jwt_required()
def update_expense(transaction_id):

    data = request.get_json()
    
    if data is None:
        return {"message": "Request body must contain JSON data."}, 400

    if "amount" not in data or "category" not in data or "date" not in data:
        return {"message": "Missing required fields."}, 400

    if not isinstance(data["amount"], int) and not isinstance(data["amount"], float):
        return {"message": "Amount must be a number."}, 400

    if not isinstance(data["category"], str):
        return {"message": "Category must be a string."}, 400

    try:
        datetime.strptime(data["date"], "%Y-%m-%d")
    except ValueError:
        return {"message": "Date must be in YYYY-MM-DD format."}, 400

    try:
        transaction_id = int(transaction_id)
    except ValueError:
        return {"message": "Transaction id must be an integer."}, 400

    conn = connect_database()
    cur = conn.cursor()
    user_id = current_user_id()
    cur.execute("""SELECT * FROM expenses WHERE transaction_id = ? AND user_id = ?""", (transaction_id, user_id))
    
    row = cur.fetchone()

    if row is None:
        conn.close()
        return {"message": "Expense not found."}, 404
    
    cur.execute("""
        UPDATE expenses
        SET amount = ?, category = ?, date = ?
        WHERE transaction_id = ? AND user_id = ?
    """, (data["amount"], data["category"], data["date"], transaction_id, user_id))
    
    conn.commit()
    conn.close()
    return {"message": "Expense updated successfully!"}



@app.route('/expenses/<transaction_id>', methods=['GET'])
@jwt_required()
def get_expense(transaction_id):

    try:
        transaction_id = int(transaction_id)
    except ValueError:
        return {"message": "Transaction id must be an integer."}, 400
    
    conn = connect_database()
    cur = conn.cursor()
    user_id = current_user_id()
    cur.execute("""SELECT * FROM expenses WHERE transaction_id = ? AND user_id = ?""", (transaction_id, user_id))
    
    row = cur.fetchone()
    
    if row is None:
        conn.close()
        return {"message": "Expense not found."}, 404
    
    expense = {
        "transaction_id": row[0],
        "amount": row[1],
        "category": row[2],
        "date": row[3]
    }

    conn.close()
    return expense



create_table()



if __name__ == "__main__":
    app.run(debug=True)
