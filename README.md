# Expense-Budget-API

A RESTful Expense and Budget Management API built with Python, Flask, and SQLite.

This project allows users to manage their own expenses and budgets, track spending, view statistics, receive budget alerts, and register/login using password hashing and JWT authentication.

## 🚀 Features

### Expense Management
- Add a new expense
- Get all expenses
- Get a single expense by transaction ID
- Update an expense
- Delete an expense
- Filter expenses by category
- Filter expenses by date
- Filter expenses by minimum amount
- Filter expenses by maximum amount
- Validate expense input data

### Budget Management
- Set a budget
- Get the current budget
- Monitor budget usage
- Calculate total amount spent
- Calculate percentage of budget used
- Receive budget alerts

### Expense Analysis
- Total number of expenses
- Total amount spent
- Average expense amount
- Highest expense
- Lowest expense
- Category-wise expense summary

### User Authentication
- User registration
- Duplicate username detection
- Password hashing using SHA-256
- User login
- Invalid username/password handling
- JWT access tokens
- User-specific expenses and budgets

### Testing
- Automated testing using pytest
- 14 automated tests covering authentication and user-data isolation

## 🛠️ Technologies Used

- Python 3
- Flask
- Flask-JWT-Extended
- SQLite
- pytest
- Git
- GitHub
- Postman

## 📁 Project Structure

Expense-Budget-API/
│
├── app.py
├── expense_budget.db
├── test_app.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── .venv/

> Note: .venv/ should not be committed to GitHub.

## ⚙️ Installation

### 1. Clone the repository

git clone https://github.com/ronakjawaliya-ux/Expense-Budget-API.git

### 2. Navigate into the project

cd Expense-Budget-API

### 3. Create a virtual environment

python -m venv .venv

### 4. Activate the virtual environment

#### Windows PowerShell

.venv\Scripts\Activate.ps1

#### Windows Command Prompt

.venv\Scripts\activate

### 5. Install dependencies

pip install -r requirements.txt

## ▶️ Running the Application

Start the Flask server:

python app.py

The API will run at:

http://127.0.0.1:5000

# 📌 API Endpoints

## 🏠 Home

### GET /

Returns a response confirming that the API is running.

Example:

GET /

## 💰 Expense Endpoints

### 1. Add Expense

POST /expenses

Adds a new expense.

Request:

{
    "amount": 500,
    "category": "Food",
    "date": "2026-08-29"
}

Response:

{
    "transaction_id": 1,
    "amount": 500,
    "category": "Food",
    "date": "2026-08-29"
}

Status Code:

200 OK

### 2. Get All Expenses

GET /expenses

Returns all expenses.

Example:

GET /expenses

Response:

[
    {
        "transaction_id": 1,
        "amount": 500,
        "category": "Food",
        "date": "2026-08-29"
    }
]

### 3. Filter Expenses by Category

GET /expenses?category=Food

Returns only expenses belonging to the specified category.

Example:

GET /expenses?category=Food

### 4. Filter Expenses by Date

GET /expenses?date=2026-08-29

Returns expenses from the specified date.

Example:

GET /expenses?date=2026-08-29

### 5. Filter by Minimum Amount

GET /expenses?min_amount=500

Returns expenses greater than or equal to the specified amount.

Example:

GET /expenses?min_amount=500

### 6. Filter by Maximum Amount

GET /expenses?max_amount=500

Returns expenses less than or equal to the specified amount.

Example:

GET /expenses?max_amount=500

### 7. Combine Filters

Multiple filters can be used together.

Example:

GET /expenses?category=Food&min_amount=500&max_amount=2000

This returns Food expenses between 500 and 2000.

### 8. Get Expense by ID

GET /expenses/<transaction_id>

Example:

GET /expenses/1

Response:

{
    "transaction_id": 1,
    "amount": 500,
    "category": "Food",
    "date": "2026-08-29"
}

If the expense does not exist:

{
    "message": "Expense not found."
}

Status Code:

404 NOT FOUND

### 9. Update Expense

PUT /expenses/<transaction_id>

Example:

PUT /expenses/1

Request:

{
    "amount": 750,
    "category": "Food",
    "date": "2026-08-29"
}

Response:

{
    "message": "Expense updated successfully!"
}

Status Code:

200 OK

### 10. Delete Expense

DELETE /expenses/<transaction_id>

Example:

DELETE /expenses/1

Response:

{
    "message": "Expense deleted successfully!"
}

Status Code:

200 OK

# 📊 Expense Statistics

## GET /expenses/statistics

Returns statistical information about expenses.

Example:

GET /expenses/statistics

Response:

{
    "total_expenses": 5,
    "total_amount": 4500,
    "average_amount": 900,
    "highest_amount": 1500,
    "lowest_amount": 300
}

# 📂 Category Summary

## GET /expenses/category-summary

Returns expenses grouped by category.

Example:

GET /expenses/category-summary

Example Response:

{
    "Food": 2500,
    "Travel": 1200,
    "Shopping": 800
}

# 💵 Budget Management

## 1. Set Budget

POST /budget

Sets the user's budget.

Request:

{
    "amount": 15000
}

Response:

{
    "message": "Budget set successfully!"
}

Status Code:

200 OK

## 2. Get Budget

GET /budget

Returns the current budget.

Example:

GET /budget

Response:

{
    "amount": 15000
}

# 🚨 Budget Alert

## GET /budget/alert

Checks the current budget usage.

Example:

GET /budget/alert

Response:

{
    "budget": 15000,
    "spent": 5000,
    "percentage_used": 33.33,
    "message": "You are within your budget."
}

The endpoint calculates how much of the budget has been spent and provides an appropriate message.

# 🔐 Authentication

## 1. Register User

POST /register

Creates a new user account.

Request:

{
    "username": "pytest_user",
    "password": "test123"
}

Successful Response:

{
    "message": "User registered successfully!"
}

Status Code:

200 OK

## Duplicate Username

If the username already exists:

{
    "message": "Username already exists."
}

Status Code:

409 CONFLICT

## 2. Login

POST /login

Authenticates a registered user.

Request:

{
    "username": "pytest_user",
    "password": "test123"
}

Successful Response:

{
    "message": "Login successful!",
    "access_token": "<JWT token>"
}

Status Code:

200 OK

## Authenticated Requests

All expense and budget endpoints require the access token returned by `/login`.
Send it in the request header:

Authorization: Bearer `<JWT token>`

Each expense and budget is stored for the authenticated user only. A user cannot view, update, or delete another user's records.

## Invalid Login

If the username or password is incorrect:

{
    "message": "Invalid username or password."
}

Status Code:

401 UNAUTHORIZED

# 🔒 Password Security

Passwords are not stored directly in the database.

The application uses Python's hashlib library with SHA-256 to generate a password hash before storing it.

Example:

password_hash = hashlib.sha256(data["password"].encode()).hexdigest()

The database stores the generated hash instead of the original password.

# 🗄️ Database

The project uses SQLite as its database.

Database file:

expense_budget.db

The application contains tables for:

- Expenses
- Budget
- Users

The database is accessed using Python's built-in sqlite3 module.

# ✅ Input Validation

The API validates incoming data before processing requests.

### Expense Validation

- Required fields
- Amount must be numeric
- Category must be a string
- Date must follow YYYY-MM-DD format

### Filter Validation

- Valid minimum amount
- Valid maximum amount
- min_amount cannot be greater than max_amount

Example error:

{
    "message": "min_amount cannot be greater than max_amount."
}

Status Code:

400 BAD REQUEST

# 🧪 Automated Testing

The project uses pytest for automated testing.

Run all tests using:

pytest

Current test result:

======================== test session starts ========================
collected 27 items

test_app.py ........................... [100%]

======================== 27 passed in 0.32s ========================

The test suite covers:

- Home endpoint
- Add expense
- Missing fields
- Invalid amount
- Invalid date
- Get expenses
- Category filtering
- Date filtering
- Minimum amount filtering
- Maximum amount filtering
- Invalid amount range
- Get expense by ID
- Invalid transaction ID
- Expense not found
- Update expense
- Delete expense
- Budget creation
- Budget retrieval
- Budget alerts
- Expense statistics
- Category summary
- User registration
- Duplicate username
- User login
- Invalid login

# 📮 Testing with Postman

The API can be tested using Postman.

Example request:

POST http://127.0.0.1:5000/expenses

Select:

Body → raw → JSON

Add this header, replacing `<JWT token>` with the token returned from `/login`:

Authorization: Bearer `<JWT token>`

Then provide:

{
    "amount": 500,
    "category": "Food",
    "date": "2026-08-29"
}

# 🧑‍💻 Development

Clone the repository and activate the virtual environment before making changes.

Run the application:

python app.py

Run tests:

pytest

Set a persistent JWT secret before running the application in a real environment:

PowerShell: `$env:JWT_SECRET_KEY = "a-long-random-secret"`

Check Git status:

git status

Add changes:

git add .

Commit changes:

git commit -m "Your commit message"

Push changes:

git push

# 📈 Project Progress

### Completed

- [x] Flask API setup
- [x] SQLite database
- [x] Expense CRUD operations
- [x] Expense validation
- [x] Expense filtering
- [x] Expense statistics
- [x] Category summary
- [x] Budget management
- [x] Budget alerts
- [x] User registration
- [x] User login
- [x] Password hashing
- [x] JWT authentication
- [x] User-specific expenses and budgets
- [x] Automated testing

# 🔮 Future Improvements

Possible future improvements include:

- [ ] Better password hashing such as bcrypt
- [ ] Pagination
- [ ] Sorting expenses
- [ ] API documentation with Swagger/OpenAPI
- [ ] More comprehensive automated tests
- [ ] Deployment
- [ ] Docker support
- [ ] Frontend integration

# 🎯 Learning Outcomes

Through this project, I practiced:

- Building REST APIs with Flask
- CRUD operations
- SQLite database integration
- SQL queries
- Dynamic SQL filtering
- Input validation
- Exception handling
- Password hashing
- User authentication
- API testing with Postman
- Automated testing with pytest
- Git and GitHub workflow
- Debugging Flask applications
- Writing maintainable backend code

# 👨‍💻 Author

Ronak Jawalia

B.Tech – Computer Science & Engineering (AIML)

GitHub:
https://github.com/ronakjawaliya-ux

LinkedIn:
https://www.linkedin.com/in/ronak-jawalia/

# ⭐ Repository

GitHub Repository:

https://github.com/ronakjawaliya-ux/Expense-Budget-API

If you found this project useful, consider giving the repository a ⭐.
