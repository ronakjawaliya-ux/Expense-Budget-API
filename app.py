from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Expense Budget API is running!"

@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.json
    return data
