from flask import Flask, request

app = Flask(__name__)

expenses = []

@app.route('/')
def home():
    return "Expense Budget API is running!"

@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.get_json()
    data["transaction_id"] = len(expenses) + 1
    expenses.append(data)
    return data


@app.route('/expenses', methods=['GET'])
def get_expenses():
    return expenses


@app.route('/expenses/<transaction_id>', methods=['DELETE'])
def delete_expense(transaction_id):
    for expense in expenses:
        if expense["transaction_id"] == int(transaction_id):
            expenses.remove(expense)
            return {"message": "Expense deleted successfully!"}

    return {"message": "Expense not found."}, 404


if __name__ == "__main__":
    app.run(debug=True)