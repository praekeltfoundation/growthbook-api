from asyncio import gather
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Any, Generic, Protocol, TypeVar

from fastapi import Depends, FastAPI, Header
from growthbook import FeatureResult as GBFeatureResult
from growthbook import Options, UserContext
from growthbook.growthbook_client import GrowthBookClient

from .models import FeatureRequest, FeatureResult


class GrowthBookClientProtocol(Protocol):
    def __init__(self, options: dict[str, Any] | Options | None) -> None: ...
    @property
    def options(self) -> Options: ...
    async def initialize(self) -> bool: ...
    async def close(self) -> None: ...
    async def eval_feature(
        self, feature_key: str, user_context: UserContext
    ) -> GBFeatureResult: ...


T = TypeVar("T", bound=GrowthBookClientProtocol)


class GrowthBookClientFactory(Generic[T]):
    def __init__(self, client_class: type[T]) -> None:
        self.client_class = client_class
        self.clients: dict[str, T] = {}

    async def get_client(self, token: str) -> T:
        if token not in self.clients:
            client = self.client_class(Options(client_key=token))
            await client.initialize()
            self.clients[token] = client
        return self.clients[token]

    async def close(self) -> None:
        await gather(*(c.close() for c in self.clients.values()))
        self.clients.clear()


gb_client_factory = GrowthBookClientFactory(GrowthBookClient)


def get_gb_client_factory() -> GrowthBookClientFactory:
    return gb_client_factory


GBClientFactoryDep = Annotated[GrowthBookClientFactory, Depends(get_gb_client_factory)]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
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
