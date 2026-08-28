from app import app


def test_home():
    client = app.test_client()

    response = client.get('/')

    assert response.status_code == 200


def test_add_expense():
    client = app.test_client()

    response = client.post('/expenses', json={
        "amount": 500,
        "category": "Food",
        "date": "2026-08-29"
    })

    assert response.status_code == 200
    assert response.json["amount"] == 500
    assert response.json["category"] == "Food"
    assert response.json["date"] == "2026-08-29"
    assert "transaction_id" in response.json


def test_add_expense_missing_fields():
    client = app.test_client()

    response = client.post('/expenses', json={
        "amount": 500,
        "category": "Food"
    })

    assert response.status_code == 400
    assert response.json["message"] == "Missing required fields."


def test_add_expense_invalid_amount():
    client = app.test_client()

    response = client.post('/expenses', json={
        "amount": "500",
        "category": "Food",
        "date": "2026-08-29"
    })

    assert response.status_code == 400
    assert response.json["message"] == "Amount must be a number."


def test_add_expense_invalid_date():
    client = app.test_client()

    response = client.post('/expenses', json={
        "amount": 500,
        "category": "Food",
        "date": "29-08-2026"
    })

    assert response.status_code == 400
    assert response.json["message"] == "Date must be in YYYY-MM-DD format."


def test_get_expenses():
    client = app.test_client()

    response = client.get('/expenses')

    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_get_expenses_by_category():
    client = app.test_client()

    response = client.get('/expenses?category=Food')

    assert response.status_code == 200

    for expense in response.json:
        assert expense["category"] == "Food"


def test_get_expenses_by_date():
    client = app.test_client()

    response = client.get('/expenses?date=2026-08-29')

    assert response.status_code == 200

    for expense in response.json:
        assert expense["date"] == "2026-08-29"


def test_get_expenses_by_min_amount():
    client = app.test_client()

    response = client.get('/expenses?min_amount=500')

    assert response.status_code == 200

    for expense in response.json:
        assert expense["amount"] >= 500


def test_get_expenses_by_max_amount():
    client = app.test_client()

    response = client.get('/expenses?max_amount=500')

    assert response.status_code == 200

    for expense in response.json:
        assert expense["amount"] <= 500


def test_get_expenses_invalid_amount_range():
    client = app.test_client()

    response = client.get('/expenses?min_amount=1000&max_amount=500')

    assert response.status_code == 400
    assert response.json["message"] == "min_amount cannot be greater than max_amount."
    
    
def test_get_expense():
    client = app.test_client()

    response = client.get('/expenses/1')

    assert response.status_code == 200
    assert response.json["transaction_id"] == 1
    
    
def test_get_expense_not_found():
    client = app.test_client()

    response = client.get('/expenses/99999')

    assert response.status_code == 404
    assert response.json["message"] == "Expense not found."
    
    
def test_get_expense_invalid_id():
    client = app.test_client()

    response = client.get('/expenses/abc')

    assert response.status_code == 400
    assert response.json["message"] == "Transaction id must be an integer."
    
    
def test_update_expense():
    client = app.test_client()

    response = client.put('/expenses/1', json={
        "amount": 750,
        "category": "Food",
        "date": "2026-08-29"
    })

    assert response.status_code == 200
    assert response.json["message"] == "Expense updated successfully!"
    
    
def test_update_expense_not_found():
    client = app.test_client()

    response = client.put('/expenses/99999', json={
        "amount": 750,
        "category": "Food",
        "date": "2026-08-29"
    })

    assert response.status_code == 404
    assert response.json["message"] == "Expense not found."
    
    
def test_delete_expense():
    client = app.test_client()

    response = client.delete('/expenses/1')

    assert response.status_code == 200
    assert response.json["message"] == "Expense deleted successfully!"
    
    
def test_delete_expense_not_found():
    client = app.test_client()

    response = client.delete('/expenses/99999')

    assert response.status_code == 404
    assert response.json["message"] == "Expense not found."
    
    
def test_set_budget():
    client = app.test_client()

    response = client.post('/budget', json={
        "amount": 15000
    })

    assert response.status_code == 200
    assert response.json["message"] == "Budget set successfully!"
    
    
def test_get_budget():
    client = app.test_client()

    response = client.get('/budget')

    assert response.status_code == 200
    assert response.json["amount"] == 15000
    
    
def test_budget_alert():
    client = app.test_client()

    response = client.get('/budget/alert')

    assert response.status_code == 200
    assert "budget" in response.json
    assert "spent" in response.json
    assert "percentage_used" in response.json
    assert "message" in response.json
    
    
def test_expense_statistics():
    client = app.test_client()

    response = client.get('/expenses/statistics')

    assert response.status_code == 200
    assert "total_expenses" in response.json
    assert "total_amount" in response.json
    assert "average_amount" in response.json
    assert "highest_amount" in response.json
    assert "lowest_amount" in response.json
    
    
def test_category_summary():
    client = app.test_client()

    response = client.get('/expenses/category-summary')

    assert response.status_code == 200
    assert isinstance(response.json, dict)
    
    
def test_register():
    client = app.test_client()

    response = client.post('/register', json={
        "username": "pytest_user",
        "password": "test123"
    })

    assert response.status_code == 200
    assert response.json["message"] == "User registered successfully!"
    
    
def test_register_duplicate_username():
    client = app.test_client()

    response = client.post('/register', json={
        "username": "pytest_user",
        "password": "test123"
    })

    assert response.status_code == 409
    assert response.json["message"] == "Username already exists."
    
    
def test_login():
    client = app.test_client()

    response = client.post('/login', json={
        "username": "pytest_user",
        "password": "test123"
    })

    assert response.status_code == 200
    assert response.json["message"] == "Login successful!"
    
    
def test_login_invalid_password():
    client = app.test_client()

    response = client.post('/login', json={
        "username": "pytest_user",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    assert response.json["message"] == "Invalid username or password."
    
    
