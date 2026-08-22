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
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(("""SELECT * FROM expenses"""))
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