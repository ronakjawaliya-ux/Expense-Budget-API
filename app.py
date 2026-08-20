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
    expenses.append(data)
    return data


@app.route('/expenses', methods=['GET'])
def get_expenses():
    return expenses


@app.route('/expenses/<transaction_id>', methods=['DELETE'])
def delete_expense(transaction_id):

    try:
        transaction_id = int(transaction_id)
    except ValueError:
        return {"message": "Transaction id must be an integer."}, 400

    for expense in expenses:
        if expense["transaction_id"] == transaction_id:
            expenses.remove(expense)
            return {"message": "Expense deleted successfully!"}

    return {"message": "Expense not found."}, 404


@app.route('/expenses/<transaction_id>', methods=['PUT'])
def update_expense(transaction_id):

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

    try:
        transaction_id = int(transaction_id)
    except ValueError:
        return {"message": "Transaction id must be an integer."}, 400

    for expense in expenses:
        if expense["transaction_id"] == transaction_id:
            expense["amount"] = data["amount"]
            expense["category"] = data["category"]
            expense["date"] = data["date"]
            return {"message": "Expense updated successfully!"}

    return {"message": "Expense not found."}, 404


@app.route('/expenses/<transaction_id>', methods=['GET'])
def get_expense(transaction_id):

    try:
        transaction_id = int(transaction_id)
    except ValueError:
        return {"message": "Transaction id must be an integer."}, 400

    for expense in expenses:
        if expense["transaction_id"] == transaction_id:
            return expense

    return {"message": "Expense not found."}, 404

create_table()

if __name__ == "__main__":
    app.run(debug=True)