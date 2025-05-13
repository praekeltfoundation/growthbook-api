from fastapi.testclient import TestClient

from growthbook_api.main import app, get_gb_client
from .fakes import FakeGrowthBookClient


def test_get_feature_value():
    fake_client = FakeGrowthBookClient()
    app.dependency_overrides[get_gb_client] = lambda: fake_client
    with TestClient(app) as client:
        response = client.post(
            "/evaluate_feature",
            json={
                "feature_key": "prototype-feature",
                "user_attributes": {"whatsapp_id": "27820001001"},
            },
        )
    assert response.status_code == 200
    assert response.json() == {
        "experiment": {
            "key": "test-experiment",
        },
        "off": False,
        "on": True,
        "ruleId": "test-ruleid",
        "source": "experiment",
        "value": "B",
    }


def test_client_initialized_and_closed():
    fake_client = FakeGrowthBookClient()
    app.dependency_overrides[get_gb_client] = lambda: fake_client
    assert not fake_client.initialized
    assert not fake_client.closed
    with TestClient(app):
        assert fake_client.initialized
        assert not fake_client.closed
    assert fake_client.initialized
    assert fake_client.closed
