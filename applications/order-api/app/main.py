import os

import httpx
from fastapi import FastAPI, HTTPException
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


@app.get("/")
def root():
    return {
        "service": "order-api",
        "status": "running",
        "version": "1.0.0",
    }


Instrumentator().instrument(app).expose(app)
