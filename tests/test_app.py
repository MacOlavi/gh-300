import copy
import pytest
from fastapi.testclient import TestClient

import src.app as app_module
from src.app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities(monkeypatch):
    """Restore the activities dict to its original state after every test."""
    original = copy.deepcopy(app_module.activities)
    yield
    monkeypatch.setattr(app_module, "activities", original)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities():
    # Arrange: no state change needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    # Arrange
    activity = "Chess Club"
    email = "new_student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert email in app_module.activities[activity]["participants"]


def test_signup_duplicate_email():
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"  # already registered in initial data

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_unknown_activity():
    # Arrange
    activity = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/unregister
# ---------------------------------------------------------------------------

def test_unregister_success():
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"  # already registered in initial data

    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert email not in app_module.activities[activity]["participants"]


def test_unregister_not_signed_up():
    # Arrange
    activity = "Chess Club"
    email = "nobody@mergington.edu"  # not registered

    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_unknown_activity():
    # Arrange
    activity = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
