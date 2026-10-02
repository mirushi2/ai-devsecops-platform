from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "AI DevSecOps Platform is running",
        "status": "success"
    }


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


def test_get_user():
    response = client.get("/users/10")

    assert response.status_code == 200
    assert response.json() == {
        "user_id": 10,
        "name": "User-10"
    }