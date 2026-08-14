import os
import sys
import pytest
import numpy as np
import flwr as fl
from fastapi.testclient import TestClient
from main import app
from database.database import init_db
from federated.client.flower_client import HospitalFLClient

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_env():
    init_db()


def test_standalone_node_cli_parser_defaults():
    from federated.client.run_hospital_node import main
    # Ensure entrypoint is importable and has main function
    assert callable(main)


def test_flower_grpc_client_compatibility():
    h_client = HospitalFLClient("hospital_1", sample_count=50)
    
    # Test Flower NumPyClient parameter exchange over network protocol representation
    params = h_client.get_parameters()
    assert isinstance(params, list)
    assert len(params) > 0
    assert isinstance(params[0], np.ndarray)

    # Test parameters updating via set_parameters
    h_client.set_parameters(params)
    assert h_client.hospital_id == "hospital_1"


def test_docker_compose_hospital_files_exist():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    dockerfile_path = os.path.join(root_dir, "Dockerfile.hospital-client")
    compose_path = os.path.join(root_dir, "docker-compose.hospital.yml")

    assert os.path.exists(dockerfile_path), "Dockerfile.hospital-client must exist"
    assert os.path.exists(compose_path), "docker-compose.hospital.yml must exist"

    with open(compose_path, "r") as f:
        content = f.read()
        assert "hospital_1_node" in content
        assert "hospital_2_node" in content
        assert "HOSPITAL_ID=hospital_1" in content


def test_websocket_reconnect_service_file_structure():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    ws_file = os.path.join(root_dir, "frontend", "src", "services", "websocket.ts")
    assert os.path.exists(ws_file)

    with open(ws_file, "r") as f:
        content = f.read()
        assert "exponential backoff" in content.lower() or "reconnectattempts" in content.lower()
        assert "Math.pow(2, reconnectAttempts" in content
