from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.main.httpx.post")
def test_create_order_success(mock_post):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "product_id": "laptop-001",
        "reserved_quantity": 2,
        "remaining_quantity": 8,
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    response = client.post(
        "/orders",
        json={"product_id": "laptop-001", "quantity": 2},
    )

    assert response.status_code == 201
    assert response.json()["status"] == "confirmed"
    assert response.json()["remaining_inventory"] == 8


@patch("app.main.httpx.post")
def test_create_order_insufficient_inventory(mock_post):
    mock_response = Mock()
    mock_response.status_code = 409
    mock_post.return_value = mock_response

    response = client.post(
        "/orders",
        json={"product_id": "laptop-001", "quantity": 20},
    )

    assert response.status_code == 409


@patch("app.main.httpx.post")
def test_create_order_product_not_found(mock_post):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_post.return_value = mock_response

    response = client.post(
        "/orders",
        json={"product_id": "missing-product", "quantity": 1},
    )

    assert response.status_code == 404


def test_create_order_invalid_quantity():
    response = client.post(
        "/orders",
        json={"product_id": "laptop-001", "quantity": 0},
    )

    assert response.status_code == 422
