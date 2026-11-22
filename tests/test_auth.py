def test_register_returns_user_without_password(client):
    response = client.post("/auth/register", json={"email": "a@example.com", "password": "password123"})
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "a@example.com"
    assert body["role"] == "user"
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email(client):
    payload = {"email": "a@example.com", "password": "password123"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400


def test_register_short_password(client):
    response = client.post("/auth/register", json={"email": "a@example.com", "password": "12345"})
    assert response.status_code == 422


def test_login_success(client):
    client.post("/auth/register", json={"email": "a@example.com", "password": "password123"})
    response = client.post("/auth/login", data={"username": "a@example.com", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "a@example.com", "password": "password123"})
    response = client.post("/auth/login", data={"username": "a@example.com", "password": "wrong-password"})
    assert response.status_code == 401


def test_me_requires_token(client):
    assert client.get("/auth/me").status_code == 401


def test_me_returns_current_user(client, auth_headers):
    headers = auth_headers("a@example.com")
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "a@example.com"


def test_users_list_forbidden_for_regular_user(client, auth_headers):
    headers = auth_headers("a@example.com")
    assert client.get("/auth/users", headers=headers).status_code == 403


def test_users_list_allowed_for_admin(client, auth_headers):
    headers = auth_headers("admin@example.com", admin=True)
    response = client.get("/auth/users", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
