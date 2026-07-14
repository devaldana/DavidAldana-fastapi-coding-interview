def test_create_user(client):
    response = client.post(
        "/users/",
        json={"first_name": "Ada", "last_name": "Lovelace"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] > 0
    assert data["first_name"] == "Ada"
    assert data["last_name"] == "Lovelace"
    assert "created_at" in data
    assert "updated_at" in data


def test_get_user_by_id(client):
    created = client.post(
        "/users/",
        json={"first_name": "Alan", "last_name": "Turing"},
    ).json()

    response = client.get(f"/users/{created['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["first_name"] == "Alan"
    assert data["last_name"] == "Turing"


def test_get_user_by_id_not_found(client):
    response = client.get("/users/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_get_all_users(client):
    assert client.get("/users/").json() == []

    client.post("/users/", json={"first_name": "Grace", "last_name": "Hopper"})
    client.post("/users/", json={"first_name": "Katherine", "last_name": "Johnson"})

    response = client.get("/users/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {u["first_name"] for u in data} == {"Grace", "Katherine"}


def test_update_user(client):
    created = client.post(
        "/users/",
        json={"first_name": "Margaret", "last_name": "Smith"},
    ).json()

    response = client.patch(
        f"/users/{created['id']}",
        json={"last_name": "Hamilton"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["first_name"] == "Margaret"  # unchanged
    assert data["last_name"] == "Hamilton"  # updated


def test_update_user_not_found(client):
    response = client.patch("/users/999999", json={"first_name": "Nobody"})

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user(client):
    created = client.post(
        "/users/",
        json={"first_name": "Dorothy", "last_name": "Vaughan"},
    ).json()

    response = client.delete(f"/users/{created['id']}")

    assert response.status_code == 200
    assert response.json()["detail"] == "User deleted"

    # The user should no longer exist.
    assert client.get(f"/users/{created['id']}").status_code == 404


def test_delete_user_not_found(client):
    response = client.delete("/users/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
