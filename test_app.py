import pytest
import app as app_module


@pytest.fixture()
def client(tmp_path):
    """Give each test an isolated database."""
    app_module.DATABASE = str(tmp_path / "test_expense_budget.db")
    app_module.app.config.update(
        TESTING=True,
        JWT_SECRET_KEY="test-secret-that-is-at-least-thirty-two-characters-long",
    )
    app_module.create_table()

    with app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def auth_headers(client):
    client.post("/register", json={"username": "test_user", "password": "test123"})
    response = client.post("/login", json={"username": "test_user", "password": "test123"})
    token = response.json["access_token"]
    return {"Authorization": f"Bearer {token}"}


def add_test_expense(client, auth_headers, amount=500, category="Food", date="2026-08-29"):
    return client.post(
        "/expenses",
        headers=auth_headers,
        json={"amount": amount, "category": category, "date": date},
    )


def test_home(client):
    assert client.get("/").status_code == 200


def test_private_route_requires_token(client):
    response = client.get("/expenses")
    assert response.status_code == 401


def test_register_and_login_returns_token(client):
    response = client.post("/register", json={"username": "new_user", "password": "test123"})
    assert response.status_code == 200

    response = client.post("/login", json={"username": "new_user", "password": "test123"})
    assert response.status_code == 200
    assert response.json["message"] == "Login successful!"
    assert "access_token" in response.json


def test_register_duplicate_username(client):
    client.post("/register", json={"username": "new_user", "password": "test123"})
    response = client.post("/register", json={"username": "new_user", "password": "test123"})
    assert response.status_code == 409
    assert response.json["message"] == "Username already exists."


def test_login_invalid_password(client):
    client.post("/register", json={"username": "new_user", "password": "test123"})
    response = client.post("/login", json={"username": "new_user", "password": "wrongpassword"})
    assert response.status_code == 401


def test_add_expense(client, auth_headers):
    response = add_test_expense(client, auth_headers)
    assert response.status_code == 200
    assert response.json["amount"] == 500
    assert response.json["category"] == "Food"
    assert "transaction_id" in response.json


def test_add_expense_validates_fields(client, auth_headers):
    response = client.post("/expenses", headers=auth_headers, json={"amount": "500"})
    assert response.status_code == 400
    assert response.json["message"] == "Missing required fields."


def test_get_expenses_and_filters(client, auth_headers):
    add_test_expense(client, auth_headers, 500, "Food")
    add_test_expense(client, auth_headers, 1000, "Travel", "2026-08-30")

    response = client.get("/expenses?category=Food&min_amount=400", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["category"] == "Food"


def test_expenses_are_private_to_the_logged_in_user(client, auth_headers):
    add_test_expense(client, auth_headers)
    client.post("/register", json={"username": "other_user", "password": "test123"})
    login = client.post("/login", json={"username": "other_user", "password": "test123"})
    other_headers = {"Authorization": f"Bearer {login.json['access_token']}"}

    response = client.get("/expenses", headers=other_headers)
    assert response.status_code == 200
    assert response.json == []


def test_get_update_and_delete_expense(client, auth_headers):
    created = add_test_expense(client, auth_headers)
    transaction_id = created.json["transaction_id"]

    response = client.get(f"/expenses/{transaction_id}", headers=auth_headers)
    assert response.status_code == 200

    response = client.put(
        f"/expenses/{transaction_id}",
        headers=auth_headers,
        json={"amount": 750, "category": "Food", "date": "2026-08-29"},
    )
    assert response.status_code == 200

    response = client.delete(f"/expenses/{transaction_id}", headers=auth_headers)
    assert response.status_code == 200


def test_expense_not_found(client, auth_headers):
    response = client.get("/expenses/99999", headers=auth_headers)
    assert response.status_code == 404


def test_expense_statistics_and_category_summary(client, auth_headers):
    add_test_expense(client, auth_headers, 500, "Food")
    add_test_expense(client, auth_headers, 1000, "Travel")

    statistics = client.get("/expenses/statistics", headers=auth_headers)
    assert statistics.status_code == 200
    assert statistics.json["total_expenses"] == 2
    assert statistics.json["total_amount"] == 1500

    summary = client.get("/expenses/category-summary", headers=auth_headers)
    assert summary.status_code == 200
    assert summary.json == {"Food": 500, "Travel": 1000}


def test_set_get_and_alert_budget(client, auth_headers):
    add_test_expense(client, auth_headers, 500)
    response = client.post("/budget", headers=auth_headers, json={"amount": 1000})
    assert response.status_code == 200

    response = client.get("/budget", headers=auth_headers)
    assert response.status_code == 200
    assert response.json["amount"] == 1000

    response = client.get("/budget/alert", headers=auth_headers)
    assert response.status_code == 200
    assert response.json["percentage_used"] == 50.0


def test_budgets_are_private_to_the_logged_in_user(client, auth_headers):
    client.post("/budget", headers=auth_headers, json={"amount": 1000})
    client.post("/register", json={"username": "other_user", "password": "test123"})
    login = client.post("/login", json={"username": "other_user", "password": "test123"})
    other_headers = {"Authorization": f"Bearer {login.json['access_token']}"}

    response = client.get("/budget", headers=other_headers)
    assert response.status_code == 404
