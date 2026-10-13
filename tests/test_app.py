import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_activity_catalog():
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert len(activities) >= 4


def test_signup_for_activity_success():
    email = "new.student@mergington.edu"
    activity_name = "Basketball Team"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_for_unknown_activity_returns_404():
    response = client.post("/activities/Unknown Activity/signup?email=student@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_duplicate_email_returns_400():
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_for_full_activity_returns_400():
    activity_name = "Basketball Team"
    app_module.activities[activity_name]["participants"] = [
        f"student{i}@mergington.edu" for i in range(app_module.activities[activity_name]["max_participants"])
    ]

    response = client.post(f"/activities/{activity_name}/signup?email=late.student@mergington.edu")

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_student_successfully():
    activity_name = "Gym Class"
    email = "john@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_for_unknown_activity_returns_404():
    response = client.delete("/activities/Unknown Activity/signup?email=student@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_non_member_returns_404():
    activity_name = "Programming Class"
    email = "not.member@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up"
