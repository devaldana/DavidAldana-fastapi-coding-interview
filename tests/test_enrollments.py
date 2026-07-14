def _make_user(client, first_name="Ada", last_name="Lovelace"):
    return client.post(
        "/users/",
        json={"first_name": first_name, "last_name": last_name},
    ).json()


def _make_course(client, title="Algorithms", description="Intro"):
    return client.post(
        "/courses/",
        json={"title": title, "description": description},
    ).json()


def test_enroll_user_in_course(client):
    user = _make_user(client)
    course = _make_course(client)

    response = client.post(
        "/enrollments/",
        json={"user_id": user["id"], "course_id": course["id"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user["id"]
    assert data["course_id"] == course["id"]
    assert "created_at" in data


def test_enroll_user_not_found(client):
    course = _make_course(client)

    response = client.post(
        "/enrollments/",
        json={"user_id": 999999, "course_id": course["id"]},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_enroll_course_not_found(client):
    user = _make_user(client)

    response = client.post(
        "/enrollments/",
        json={"user_id": user["id"], "course_id": 999999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_enroll_duplicate(client):
    user = _make_user(client)
    course = _make_course(client)

    payload = {"user_id": user["id"], "course_id": course["id"]}
    assert client.post("/enrollments/", json=payload).status_code == 200

    response = client.post("/enrollments/", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "User is already enrolled in this course"


def test_user_cannot_exceed_five_courses(client):
    user = _make_user(client)
    courses = [_make_course(client, title=f"Course {i}") for i in range(6)]

    # First 5 enrollments succeed.
    for course in courses[:5]:
        response = client.post(
            "/enrollments/",
            json={"user_id": user["id"], "course_id": course["id"]},
        )
        assert response.status_code == 200

    # The 6th is rejected.
    response = client.post(
        "/enrollments/",
        json={"user_id": user["id"], "course_id": courses[5]["id"]},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "User cannot be enrolled in more than 5 courses"


def test_course_cannot_exceed_twenty_users(client):
    course = _make_course(client)
    users = [_make_user(client, first_name=f"User{i}") for i in range(21)]

    # First 20 enrollments succeed.
    for user in users[:20]:
        response = client.post(
            "/enrollments/",
            json={"user_id": user["id"], "course_id": course["id"]},
        )
        assert response.status_code == 200

    # The 21st is rejected.
    response = client.post(
        "/enrollments/",
        json={"user_id": users[20]["id"], "course_id": course["id"]},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Course cannot have more than 20 users"


def test_get_all_enrollments(client):
    assert client.get("/enrollments/").json() == []

    user = _make_user(client)
    course = _make_course(client)
    client.post(
        "/enrollments/",
        json={"user_id": user["id"], "course_id": course["id"]},
    )

    response = client.get("/enrollments/")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_courses_for_user(client):
    user = _make_user(client)
    course_a = _make_course(client, title="A")
    course_b = _make_course(client, title="B")

    for course in (course_a, course_b):
        client.post(
            "/enrollments/",
            json={"user_id": user["id"], "course_id": course["id"]},
        )

    response = client.get(f"/enrollments/users/{user['id']}/courses")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {e["course_id"] for e in data} == {course_a["id"], course_b["id"]}


def test_get_courses_for_user_not_found(client):
    response = client.get("/enrollments/users/999999/courses")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_get_users_for_course(client):
    course = _make_course(client)
    user_a = _make_user(client, first_name="Alan")
    user_b = _make_user(client, first_name="Grace")

    for user in (user_a, user_b):
        client.post(
            "/enrollments/",
            json={"user_id": user["id"], "course_id": course["id"]},
        )

    response = client.get(f"/enrollments/courses/{course['id']}/users")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {e["user_id"] for e in data} == {user_a["id"], user_b["id"]}


def test_get_users_for_course_not_found(client):
    response = client.get("/enrollments/courses/999999/users")

    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_unenroll(client):
    user = _make_user(client)
    course = _make_course(client)
    payload = {"user_id": user["id"], "course_id": course["id"]}
    client.post("/enrollments/", json=payload)

    response = client.request("DELETE", "/enrollments/", json=payload)

    assert response.status_code == 200
    assert response.json()["detail"] == "Enrollment deleted"
    assert client.get("/enrollments/").json() == []


def test_unenroll_not_found(client):
    user = _make_user(client)
    course = _make_course(client)

    response = client.request(
        "DELETE",
        "/enrollments/",
        json={"user_id": user["id"], "course_id": course["id"]},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Enrollment not found"
