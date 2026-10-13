from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)
original_activities = deepcopy(activities)


def setup_function():
    activities.clear()
    activities.update(deepcopy(original_activities))


def test_signup_success():
    response = client.post("/activities/Chess Club/signup", params={"email": "alex@mergington.edu"})

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up alex@mergington.edu for Chess Club"}
    assert "alex@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_rejects_unknown_activity():
    response = client.post("/activities/Unknown Activity/signup", params={"email": "alex@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_student():
    response = client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_rejects_when_activity_is_full():
    target_activity = activities["Basketball Team"]
    target_activity["participants"] = [
        f"student-{index}@mergington.edu"
        for index in range(target_activity["max_participants"])
    ]

    response = client.post("/activities/Basketball Team/signup", params={"email": "extra@mergington.edu"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_success():
    response = client.delete("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})

    assert response.status_code == 200
    assert response.json() == {"message": "Unregistered michael@mergington.edu from Chess Club"}
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_rejects_unknown_activity():
    response = client.delete("/activities/Unknown Activity/signup", params={"email": "alex@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_student_not_signed_up():
    response = client.delete("/activities/Chess Club/signup", params={"email": "not-registered@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up"
