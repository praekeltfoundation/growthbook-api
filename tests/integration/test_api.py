from collections.abc import Generator

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from growthbook_api.main import GrowthBookClientFactory, app, get_gb_client_factory
from tests.fakes import FakeGrowthBookClient


@pytest.fixture
def gb_client_factory() -> Generator[GrowthBookClientFactory]:
    """
    Fake GrowthBook client.
    """
    fake_factory = GrowthBookClientFactory(FakeGrowthBookClient)
    app.dependency_overrides[get_gb_client_factory] = lambda: fake_factory
    yield fake_factory
    del app.dependency_overrides[get_gb_client_factory]


@pytest.fixture
def api_client(gb_client_factory: GrowthBookClientFactory) -> Generator[TestClient]:  # noqa: ARG001
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
        headers={"CLIENT-TOKEN": "faketoken"},
        json={
            "feature_key": "prototype-feature",
            "user_attributes": {"whatsapp_id": "27820001001"},
        },
    )
    assert response.status_code == status.HTTP_200_OK
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


def test_client_initialized_and_closed(
    gb_client_factory: GrowthBookClientFactory,
) -> None:
    """
    The application should create and initialize clients on request, and close it on
    shutdown
    """
    assert "faketoken" not in gb_client_factory.clients
    with TestClient(app) as client:
        client.post(
            "/evaluate_feature",
            headers={"CLIENT-TOKEN": "faketoken"},
            json={
                "feature_key": "prototype-feature",
                "user_attributes": {"whatsapp_id": "27820001001"},
            },
        )
        assert "faketoken" in gb_client_factory.clients
        gb_client = gb_client_factory.clients["faketoken"]
        assert gb_client.initialized
        assert not gb_client.closed
    assert gb_client.initialized
    assert gb_client.closed
    assert gb_client.options.client_key == "faketoken"
