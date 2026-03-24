import os
import json
import pytest
from unittest.mock import patch, MagicMock

# Import the Flask app from main.py
from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_missing_payload(client):
    """Test when no payload is provided."""
    response = client.post('/', json={})
    assert response.status_code == 400
    assert b"Invalid event data" in response.data

def test_missing_env_vars(client, monkeypatch):
    """Test when PROJECT_ID or DATASTORE_ID are missing."""
    # Ensure they are unset
    monkeypatch.delenv('PROJECT_ID', raising=False)
    monkeypatch.delenv('DATASTORE_ID', raising=False)
    
    payload = {
        "bucket": "test-bucket",
        "name": "test-file.pdf"
    }
    
    with patch('main.discoveryengine.DocumentServiceClient'):
        response = client.post('/', json=payload)
        
    assert response.status_code == 500
    assert b"Missing PROJECT_ID" in response.data

def test_successful_trigger(client, monkeypatch):
    """Test successful parsing and Vertex AI API call."""
    # Set fake environment variables
    monkeypatch.setenv('PROJECT_ID', 'gen-lang-client-0436480880')
    monkeypatch.setenv('DATASTORE_ID', 'test-datastore-123')
    
    payload = {
        "bucket": "test-bucket",
        "name": "test-file.pdf"
    }
    
    # Mock the Discovery Engine client
    with patch('main.discoveryengine.DocumentServiceClient') as mock_client_class:
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        
        response = client.post('/', json=payload)
        
        assert response.status_code == 200
        assert b"Indexing started for gs://test-bucket/test-file.pdf" in response.data
        
        # Verify the import request was made with correct arguments
        mock_instance.import_documents.assert_called_once()
        call_args = mock_instance.import_documents.call_args[1]
        request_obj = call_args['request']
        assert "gen-lang-client-0436480880" in request_obj.parent
        assert "test-datastore-123" in request_obj.parent
        assert request_obj.gcs_source.input_uris == ["gs://test-bucket/test-file.pdf"]
