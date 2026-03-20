import pytest
from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_health_endpoint_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@patch("backend.main.db")
def test_cameras_endpoint_returns_list(mock_db):
    mock_db.collection.return_value.stream.return_value = []
    response = client.get("/cameras")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@patch("backend.main.db")
def test_single_camera_returns_correct_fields(mock_db):
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"cam_id": "TEST"}
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
    
    response = client.get("/cameras/TEST")
    assert response.status_code == 200
    assert response.json().get("cam_id") == "TEST"

@patch("backend.main.db")
def test_invalid_camera_returns_404(mock_db):
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
    
    response = client.get("/cameras/INVALID")
    assert response.status_code == 404

@patch("backend.main.genai.Client")
def test_assistant_endpoint_accepts_message(mock_client):
    mock_response = MagicMock()
    mock_response.text = "Hello"
    mock_client.return_value.models.generate_content.return_value = mock_response
    
    response = client.post("/assistant", json={"message": "hi", "context": {}})
    assert response.status_code == 200

def test_broadcast_generates_audio():
    response = client.post("/broadcast", json={
        "cam_id": "C1", "incident_type": "Crash", "severity": 5, "address": "Road", "units": []
    })
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"

@patch("backend.main.db")
def test_incident_post_writes_to_firestore(mock_db):
    mock_doc_ref = MagicMock()
    mock_doc_ref.id = "123"
    mock_db.collection.return_value.document.return_value = mock_doc_ref
    
    response = client.post("/cameras/CAM-001/incident", json={"data": {"foo": "bar"}})
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_pii_masking_runs_on_frame():
    from backend.services.video_service import apply_pii_masking
    import numpy as np
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    masked = apply_pii_masking(frame)
    assert masked.shape == frame.shape
