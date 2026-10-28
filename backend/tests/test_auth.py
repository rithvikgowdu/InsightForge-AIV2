from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User


def test_user_registration_success(client: TestClient):
    payload = {
        "email": "newdev@example.com",
        "username": "newdev",
        "password": "SecurePassword123!",
        "full_name": "New Developer",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newdev@example.com"
    assert data["username"] == "newdev"
    assert "id" in data
    assert "password" not in data


def test_user_registration_duplicate_email(client: TestClient, test_user: User):
    payload = {
        "email": test_user.email,
        "username": "different_username",
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_user_registration_duplicate_username(client: TestClient, test_user: User):
    payload = {
        "email": "different_email@example.com",
        "username": test_user.username,
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert "already taken" in response.json()["detail"]


def test_user_login_success(client: TestClient, test_user: User):
    # Login with username
    response = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": test_user.username, "password": "Password123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == test_user.username

    # Login with email
    response2 = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": test_user.email, "password": "Password123!"},
    )
    assert response2.status_code == 200


def test_user_login_invalid_password(client: TestClient, test_user: User):
    response = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": test_user.username, "password": "WrongPassword99!"},
    )
    assert response.status_code == 401
    assert "Invalid username/email or password" in response.json()["detail"]


def test_user_login_nonexistent(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "nonexistent_user", "password": "Password123!"},
    )
    assert response.status_code == 401


def test_get_current_user_profile(client: TestClient, auth_headers: dict, test_user: User):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["username"] == test_user.username


def test_protected_route_missing_token(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_protected_route_invalid_token(client: TestClient):
    headers = {"Authorization": "Bearer invalid_garbage_token"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401

