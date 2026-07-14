def test_create_course(client):
    response = client.post(
        "/courses/",
        json={"title": "Algorithms", "description": "Intro to algorithms"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] > 0
    assert data["title"] == "Algorithms"
    assert data["description"] == "Intro to algorithms"
    assert "created_at" in data
    assert "updated_at" in data


def test_get_course_by_id(client):
    created = client.post(
        "/courses/",
        json={"title": "Databases", "description": "Relational databases"},
    ).json()

    response = client.get(f"/courses/{created['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["title"] == "Databases"
    assert data["description"] == "Relational databases"


def test_get_course_by_id_not_found(client):
    response = client.get("/courses/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_get_all_courses(client):
    assert client.get("/courses/").json() == []

    client.post("/courses/", json={"title": "Networks", "description": "TCP/IP"})
    client.post("/courses/", json={"title": "Compilers", "description": "Parsing"})

    response = client.get("/courses/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {c["title"] for c in data} == {"Networks", "Compilers"}


def test_update_course(client):
    created = client.post(
        "/courses/",
        json={"title": "Operating Systems", "description": "Old description"},
    ).json()

    response = client.patch(
        f"/courses/{created['id']}",
        json={"description": "Processes and threads"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["title"] == "Operating Systems"  # unchanged
    assert data["description"] == "Processes and threads"  # updated


def test_update_course_not_found(client):
    response = client.patch("/courses/999999", json={"title": "Nobody"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_delete_course(client):
    created = client.post(
        "/courses/",
        json={"title": "Graphics", "description": "Rendering"},
    ).json()

    response = client.delete(f"/courses/{created['id']}")

    assert response.status_code == 200
    assert response.json()["detail"] == "Course deleted"

    # The course should no longer exist.
    assert client.get(f"/courses/{created['id']}").status_code == 404


def test_delete_course_not_found(client):
    response = client.delete("/courses/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"
