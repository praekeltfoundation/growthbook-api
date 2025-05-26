import pytest
from growthbook.growthbook_client import FeatureRefreshStrategy

from growthbook_api.main import GrowthBookClientFactory
from tests.fakes import FakeGrowthBookClient


@pytest.mark.asyncio
async def test_get_client() -> None:
    """
    Getting a client should create and initialize a client with the correct options
    """
    factory = GrowthBookClientFactory(FakeGrowthBookClient)
    client = await factory.get_client("faketoken")
    assert client.options.client_key == "faketoken"
    assert client.options.refresh_strategy == FeatureRefreshStrategy.SERVER_SENT_EVENTS
    assert client.initialized
    assert not client.closed


@pytest.mark.asyncio
async def test_get_cached_client() -> None:
    """
    Getting a client with the same config twice should return the same client
    """
    factory = GrowthBookClientFactory(FakeGrowthBookClient)
    client1 = await factory.get_client("faketoken")
    client2 = await factory.get_client("faketoken")
    assert client1 == client2
