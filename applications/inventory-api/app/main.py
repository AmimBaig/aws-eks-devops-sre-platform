import os

import redis
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel


app = FastAPI(
    title="Inventory API",
    description="Inventory management service for the DevOps/SRE platform project",
    version="1.0.0",
)


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
)


class InventoryReservation(BaseModel):
    quantity: int


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/ready")
def readiness_check():
    try:
        redis_client.ping()
        return {"status": "ready"}
    except redis.RedisError:
        raise HTTPException(
            status_code=503,
            detail="Redis is unavailable",
        )


@app.get("/inventory/{product_id}")
def get_inventory(product_id: str):
    quantity = redis_client.get(f"inventory:{product_id}")

    if quantity is None:
        return {
            "product_id": product_id,
            "quantity": 0,
        }

    return {
        "product_id": product_id,
        "quantity": int(quantity),
    }


@app.post("/inventory/{product_id}/reserve")
def reserve_inventory(
    product_id: str,
    reservation: InventoryReservation,
):
    if reservation.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero",
        )

    key = f"inventory:{product_id}"
    current_quantity = redis_client.get(key)

    if current_quantity is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    current_quantity = int(current_quantity)

    if current_quantity < reservation.quantity:
        raise HTTPException(
            status_code=409,
            detail="Insufficient inventory",
        )

    new_quantity = current_quantity - reservation.quantity
    redis_client.set(key, new_quantity)

    return {
        "product_id": product_id,
        "reserved_quantity": reservation.quantity,
        "remaining_quantity": new_quantity,
    }


@app.get("/")
def root():
    return {
        "service": "inventory-api",
        "status": "running",
        "version": "1.0.0",
    }


Instrumentator().instrument(app).expose(app)
