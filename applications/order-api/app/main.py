import os
import uuid

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI(
    title="Order API",
    description="Order management service for the DevOps/SRE platform project",
    version="1.0.0",
)

INVENTORY_API_URL = os.getenv(
    "INVENTORY_API_URL",
    "http://localhost:8001",
)


class OrderRequest(BaseModel):
    product_id: str = Field(min_length=1)
    quantity: int = Field(gt=0)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/ready")
def readiness_check():
    return {"status": "ready"}


@app.get("/inventory/{product_id}/availability")
def check_inventory_availability(product_id: str):
    try:
        response = httpx.get(
            f"{INVENTORY_API_URL}/inventory/{product_id}",
            timeout=5.0,
        )
        response.raise_for_status()
        inventory = response.json()

        return {
            "product_id": product_id,
            "available": inventory["quantity"] > 0,
            "quantity": inventory["quantity"],
        }

    except httpx.HTTPError:
        raise HTTPException(
            status_code=503,
            detail="Inventory service unavailable",
        )


@app.post("/orders", status_code=201)
def create_order(order: OrderRequest):
    try:
        response = httpx.post(
            f"{INVENTORY_API_URL}/inventory/"
            f"{order.product_id}/reserve",
            json={"quantity": order.quantity},
            timeout=5.0,
        )

        if response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

        if response.status_code == 409:
            raise HTTPException(
                status_code=409,
                detail="Insufficient inventory",
            )

        response.raise_for_status()
        reservation = response.json()

        return {
            "order_id": str(uuid.uuid4()),
            "product_id": order.product_id,
            "quantity": order.quantity,
            "status": "confirmed",
            "remaining_inventory": reservation["remaining_quantity"],
        }

    except HTTPException:
        raise

    except httpx.HTTPError:
        raise HTTPException(
            status_code=503,
            detail="Inventory service unavailable",
        )


@app.get("/")
def root():
    return {
        "service": "order-api",
        "status": "running",
        "version": "1.0.0",
    }


Instrumentator().instrument(app).expose(app)
