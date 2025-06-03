"""Entry point for python -m prometheus"""
from prometheus.api.app import app
import uvicorn
import os

if __name__ == "__main__":
    # Port must be set via environment variable
    port = int(os.environ.get("PROMETHEUS_PORT"))
    uvicorn.run(app, host="0.0.0.0", port=port)