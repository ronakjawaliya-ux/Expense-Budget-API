from flask import Flask, request

app = Flask(__name__)

expenses = []

@app.route('/')
def home():
    return "Expense Budget API is running!"

@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.json
    expenses.append(data)
    return data

@app.route('/expenses', methods=['GET'])
def get_expenses():
    return expenses



if __name__ == "__main__":
    app.run(debug=True)