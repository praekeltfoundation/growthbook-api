from asyncio import gather
from collections.abc import Generator
from contextlib import asynccontextmanager
from typing import Annotated, TypeVar

from fastapi import Depends, FastAPI, Header
from growthbook import Options, UserContext
from growthbook.growthbook_client import GrowthBookClient

from .models import FeatureRequest, FeatureResult

ClientCls = TypeVar("ClientCls")


class GrowthBookClientFactory:
    def __init__(self, client_class: ClientCls = GrowthBookClient) -> None:
        self.client_class = client_class
        self.clients: dict[str, GrowthBookClient] = {}

    async def get_client(self, token: str) -> ClientCls:
        if token not in self.clients:
            client = self.client_class(Options(client_key=token))
            await client.initialize()
            self.clients[token] = client
        return self.clients[token]

    async def close(self) -> None:
        await gather(*(c.close() for c in self.clients.values()))
        self.clients.clear()


gb_client_factory = GrowthBookClientFactory()


def get_gb_client_factory() -> GrowthBookClientFactory:
    return gb_client_factory


GBClientFactoryDep = Annotated[GrowthBookClientFactory, Depends(get_gb_client_factory)]


@asynccontextmanager
async def lifespan(app: FastAPI) -> Generator:
    # FastAPI doesn't support dependancies in lifespans, so we fetch it manually
    factory = app.dependency_overrides.get(
        get_gb_client_factory, get_gb_client_factory
    )()
    yield
    await factory.close()


app = FastAPI(lifespan=lifespan)


@app.post("/evaluate_feature")
async def evaluate_feature(
    client_token: Annotated[str, Header()],
    feature_request: FeatureRequest,
    gb_client_factory: GBClientFactoryDep,
) -> FeatureResult:
    gb_client = await gb_client_factory.get_client(client_token)
    context = UserContext(attributes=feature_request.user_attributes)
    result = await gb_client.eval_feature(feature_request.feature_key, context)
    return FeatureResult.model_validate(result.to_dict())
