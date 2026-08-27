from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="Order API",
    description="Order management service for the DevOps/SRE platform project",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/ready")
def readiness_check():
    return {"status": "ready"}


@app.get("/")
def root():
    return {
        "service": "order-api",
        "status": "running",
        "version": "1.0.0",
    }


Instrumentator().instrument(app).expose(app)
