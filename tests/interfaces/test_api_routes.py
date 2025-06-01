import pytest
from fastapi.testclient import TestClient

# Assuming your FastAPI app instance is in 'app.main.app'
# If not, you'll need to adjust the import path accordingly.
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    # You might want to assert the response content as well, e.g.:
    # assert response.json() == {"status": "ok"}
