"""Tests for the FastAPI REST API endpoints."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.api.main import app


@pytest.fixture
def transport():
    return ASGITransport(app=app)


@pytest_asyncio.fixture
async def client(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """GET /api/health should return status ok."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_get_robot_state(client):
    """GET /api/robot/state should return joint angles and end-effector position."""
    response = await client.get("/api/robot/state")
    assert response.status_code == 200
    data = response.json()
    assert "joint_angles_deg" in data
    assert "end_effector" in data
    assert len(data["joint_angles_deg"]) == 5
    assert "x" in data["end_effector"]
    assert "y" in data["end_effector"]
    assert "z" in data["end_effector"]


@pytest.mark.asyncio
async def test_write_text(client):
    """POST /api/writer/simulate with text should return simulation data."""
    response = await client.post(
        "/api/writer/simulate",
        json={"text": "HI"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "HI"
    assert "action_log" in data
    assert "simulation" in data
    assert data["summary"]["characters_placed"] == 2


@pytest.mark.asyncio
async def test_forward_kinematics_endpoint(client):
    """POST /api/kinematics/forward should return end-effector position."""
    response = await client.post(
        "/api/kinematics/forward",
        json={"angles_deg": [0, 0, 0, 0, 0], "gripper_mm": 0.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert "end_effector" in data
    assert data["end_effector"]["x"] > 0


@pytest.mark.asyncio
async def test_inverse_kinematics_endpoint(client):
    """POST /api/kinematics/inverse should return joint angles."""
    response = await client.post(
        "/api/kinematics/inverse",
        json={"x": 300.0, "y": 0.0, "z": 50.0, "approach_angle_deg": -70.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert "angles_deg" in data
    assert len(data["angles_deg"]) == 5


@pytest.mark.asyncio
async def test_writer_config_endpoint(client):
    """GET /api/writer/config should return configuration defaults."""
    response = await client.get("/api/writer/config")
    assert response.status_code == 200
    data = response.json()
    assert "block_circle" in data
    assert "writing_line" in data
    assert "robot" in data


@pytest.mark.asyncio
async def test_write_invalid_empty_text(client):
    """POST /api/writer/simulate with empty text should fail validation."""
    response = await client.post(
        "/api/writer/simulate",
        json={"text": ""},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_hardware_status_disconnected(client):
    """GET /api/hardware/status should report disconnected by default."""
    response = await client.get("/api/hardware/status")
    assert response.status_code == 200
    data = response.json()
    assert data["connected"] is False


@pytest.mark.asyncio
async def test_trajectory_frames_default(client):
    """GET /api/trajectory-frames should return animation frames."""
    response = await client.get("/api/trajectory-frames", params={"text": "HI"})
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "HI"
    assert data["total_steps"] > 0
    assert data["n_frames"] > 0
    assert len(data["frames"]) == data["n_frames"]

    # Verify frame structure
    frame = data["frames"][0]
    assert "joint_angles_deg" in frame
    assert len(frame["joint_angles_deg"]) == 5
    assert "joint_positions" in frame
    assert "end_effector" in frame
    assert "x" in frame["end_effector"]
    assert "gripper_mm" in frame
    assert "timestamp" in frame


@pytest.mark.asyncio
async def test_trajectory_frames_with_step(client):
    """GET /api/trajectory-frames with frame_step should subsample."""
    response_all = await client.get(
        "/api/trajectory-frames", params={"text": "A", "frame_step": 1}
    )
    response_skip = await client.get(
        "/api/trajectory-frames", params={"text": "A", "frame_step": 10}
    )
    assert response_all.status_code == 200
    assert response_skip.status_code == 200
    n_all = response_all.json()["n_frames"]
    n_skip = response_skip.json()["n_frames"]
    assert n_skip <= n_all, "Subsampled frames should be fewer or equal"


@pytest.mark.asyncio
async def test_trajectory_frames_empty_text(client):
    """GET /api/trajectory-frames with empty text should fail."""
    response = await client.get("/api/trajectory-frames", params={"text": ""})
    assert response.status_code == 400
