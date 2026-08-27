from flask import Flask, request
from datetime import datetime
import sqlite3


app = Flask(__name__)

DATABASE = "expense_budget.db"

def connect_database():
    conn = sqlite3.connect(DATABASE)
    return conn


def create_table():
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS expenses (
                       transaction_id INTEGER PRIMARY KEY,
                       amount REAL ,
                       category TEXT ,
                       date TEXT 
                       )
                """)

    conn.commit()
    conn.close()


@app.route('/')
def home():
    return "Expense Budget API is running!"


@app.route('/expenses', methods=['POST'])
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
    
    cur.execute("""INSERT INTO expenses (amount, category, date)
               VALUES (?, ?, ?)""",
                (data["amount"], data["category"], data["date"])
                )
    
    conn.commit()
    transaction_id = cur.lastrowid
    data["transaction_id"] = transaction_id
    return data



@app.route('/expenses', methods=['GET'])
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
    
    query = "SELECT * FROM expenses WHERE 1=1"
    params = []
    
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
def expense_statistics():
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("""SELECT COUNT(*), SUM(amount), AVG(amount), MAX(amount), MIN(amount)
                FROM expenses""")
    
    row = cur.fetchone()
    conn.close()
    
    return {"total_expenses": row[0],
            "total_amount": row[1],
            "average_amount": row[2],
            "highest_amount": row[3],
            "lowest_amount": row[4]
    }



@app.route('/expenses/category-summary', methods=['GET'])
def category_summary():
    conn = connect_database()
    cur = conn.cursor()

    cur.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        GROUP BY category
    """)

    rows = cur.fetchall()
    conn.close()

    category_data = {}

    for row in rows:
        category_data[row[0]] = row[1]

    return category_data



@app.route('/expenses/<transaction_id>', methods=['DELETE'])
def delete_expense(transaction_id):

    try:
        transaction_id = int(transaction_id)
    except ValueError:
        return {"message": "Transaction id must be an integer."}, 400
    
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(
    """SELECT * FROM expenses WHERE transaction_id = ?""", (transaction_id,))
    
    row = cur.fetchone()
    
    if row is None:
        conn.close()
        return {"message": "Expense not found."}, 404
    
    cur.execute(
    """DELETE FROM expenses WHERE transaction_id = ?""", (transaction_id,))

    conn.commit()
    conn.close()
    
    return{"message": "Expense deleted successfully!"}



@app.route('/expenses/<transaction_id>', methods=['PUT'])
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
    cur.execute("""SELECT * FROM expenses WHERE transaction_id = ?""", (transaction_id,))
    
    row = cur.fetchone()

    if row is None:
        conn.close()
        return {"message": "Expense not found."}, 404
    
    cur.execute("""
        UPDATE expenses
        SET amount = ?, category = ?, date = ?
        WHERE transaction_id = ?
    """, (data["amount"], data["category"], data["date"], transaction_id))
    
    conn.commit()
    conn.close()
    return {"message": "Expense updated successfully!"}


@app.route('/expenses/<transaction_id>', methods=['GET'])
def get_expense(transaction_id):

    try:
        transaction_id = int(transaction_id)
    except ValueError:
        return {"message": "Transaction id must be an integer."}, 400
    
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("""SELECT * FROM expenses WHERE transaction_id = ?""", (transaction_id,))
    
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