from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

expenses = []
next_transaction_id = 1

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

    global next_transaction_id
    data["transaction_id"] = next_transaction_id
    next_transaction_id +=1
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


if __name__ == "__main__":
    app.run(debug=True)