
import pytest
from app import create_app
from database.db import db


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        db.reset()
        yield client
        db.reset()


def test_healthcheck_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "UP"
    assert "Enterprise Smart Library" in json_data["service"]


def test_api_list_books(client):
    response = client.get("/api/books")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["count"] >= 2


def test_api_borrow_endpoint(client):
    payload = {"user_id": "U101", "book_id": "B001"}
    response = client.post("/api/borrow", json=payload)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Book checked out successfully"
