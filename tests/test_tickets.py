def create_ticket(client, headers, title="Не работает вход"):
    return client.post(
        "/tickets",
        json={"title": title, "description": "Пишет ошибку"},
        headers=headers,
    )


def test_create_ticket_enqueues_notification(client, auth_headers, enqueued):
    headers = auth_headers("a@example.com")
    response = create_ticket(client, headers)
    assert response.status_code == 201
    assert enqueued == [response.json()["id"]]


def test_create_ticket_requires_auth(client):
    response = client.post("/tickets", json={"title": "abc", "description": "x"})
    assert response.status_code == 401


def test_user_sees_only_own_tickets(client, auth_headers):
    first = auth_headers("a@example.com")
    second = auth_headers("b@example.com")
    create_ticket(client, first, "Заявка A")
    create_ticket(client, second, "Заявка B")
    response = client.get("/tickets", headers=first)
    assert [t["title"] for t in response.json()] == ["Заявка A"]


def test_admin_sees_all_tickets(client, auth_headers):
    user = auth_headers("a@example.com")
    admin = auth_headers("admin@example.com", admin=True)
    create_ticket(client, user)
    assert len(client.get("/tickets", headers=admin).json()) == 1


def test_foreign_ticket_is_hidden(client, auth_headers):
    owner = auth_headers("a@example.com")
    stranger = auth_headers("b@example.com")
    ticket_id = create_ticket(client, owner).json()["id"]
    assert client.get(f"/tickets/{ticket_id}", headers=stranger).status_code == 404


def test_status_change_forbidden_for_user(client, auth_headers):
    headers = auth_headers("a@example.com")
    ticket_id = create_ticket(client, headers).json()["id"]
    response = client.patch(f"/tickets/{ticket_id}/status", json={"status": "closed"}, headers=headers)
    assert response.status_code == 403


def test_status_change_allowed_for_admin(client, auth_headers):
    user = auth_headers("a@example.com")
    admin = auth_headers("admin@example.com", admin=True)
    ticket_id = create_ticket(client, user).json()["id"]
    response = client.patch(f"/tickets/{ticket_id}/status", json={"status": "in_progress"}, headers=admin)
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_invalid_status_rejected(client, auth_headers):
    user = auth_headers("a@example.com")
    admin = auth_headers("admin@example.com", admin=True)
    ticket_id = create_ticket(client, user).json()["id"]
    response = client.patch(f"/tickets/{ticket_id}/status", json={"status": "abc"}, headers=admin)
    assert response.status_code == 422


def test_comments_flow(client, auth_headers):
    headers = auth_headers("a@example.com")
    ticket_id = create_ticket(client, headers).json()["id"]
    created = client.post(f"/tickets/{ticket_id}/comments", json={"text": "Подробности"}, headers=headers)
    assert created.status_code == 201
    listed = client.get(f"/tickets/{ticket_id}/comments", headers=headers)
    assert [c["text"] for c in listed.json()] == ["Подробности"]


def test_admin_can_delete_ticket(client, auth_headers):
    user = auth_headers("a@example.com")
    admin = auth_headers("admin@example.com", admin=True)
    ticket_id = create_ticket(client, user).json()["id"]
    assert client.delete(f"/tickets/{ticket_id}", headers=admin).status_code == 204
    assert client.get(f"/tickets/{ticket_id}", headers=admin).status_code == 404
