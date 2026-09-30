from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_readiness_check():
    response = client.get("/ready")

    assert response.status_code in (200, 503)

def test_reserve_inventory_success(monkeypatch):
    from app.main import redis_client

    monkeypatch.setattr(redis_client, "eval", lambda *args: 7)

    response = client.post(
        "/inventory/order-test/reserve",
        json={"quantity": 3},
    )

    assert response.status_code == 200
    assert response.json() == {
        "product_id": "order-test",
        "reserved_quantity": 3,
        "remaining_quantity": 7,
    }


def test_reserve_inventory_insufficient(monkeypatch):
    from app.main import redis_client

    monkeypatch.setattr(redis_client, "eval", lambda *args: -2)

    response = client.post(
        "/inventory/order-test/reserve",
        json={"quantity": 3},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Insufficient inventory"


def test_reserve_inventory_missing_product(monkeypatch):
    from app.main import redis_client

    monkeypatch.setattr(redis_client, "eval", lambda *args: -1)

    response = client.post(
        "/inventory/order-test/reserve",
        json={"quantity": 3},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"
