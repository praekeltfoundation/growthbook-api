import pytest
from fastapi import status
from fastapi.testclient import TestClient

from growthbook_api.main import app, get_gb_client

from .fakes import FakeGrowthBookClient


@pytest.fixture
def gb_client() -> None:
    """
    Fake GrowthBook client.
    """
    fake_client = FakeGrowthBookClient()
    app.dependency_overrides[get_gb_client] = lambda: fake_client
    yield fake_client
    del app.dependency_overrides[get_gb_client]


@pytest.fixture
def api_client(gb_client: FakeGrowthBookClient) -> TestClient:  # noqa: ARG001
    """
    Test client for application with fake GrowthBook client.
    """
    with TestClient(app) as client:
        yield client


def test_get_feature_value(api_client: TestClient) -> None:
    """
    The evaluate_feature endpoint should evaluate the feature and return the relevant
    results.
    """
    response = api_client.post(
        "/evaluate_feature",
        json={
            "feature_key": "prototype-feature",
            "user_attributes": {"whatsapp_id": "27820001001"},
        },
    )
    assert response.status_code == status.OK
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


def test_client_initialized_and_closed(gb_client: FakeGrowthBookClient) -> None:
    """
    The application should initialize the GrowthBook client on startup, and close it
    on shutdown.
    """
    assert not gb_client.initialized
    assert not gb_client.closed
    with TestClient(app):
        assert gb_client.initialized
        assert not gb_client.closed
    assert gb_client.initialized
    assert gb_client.closed
