from collections.abc import Generator
from contextlib import asynccontextmanager
from os import environ
from typing import Annotated

from fastapi import Depends, FastAPI
from growthbook import Options, UserContext
from growthbook.growthbook_client import GrowthBookClient

from .models import FeatureRequest, FeatureResult

gb_client = GrowthBookClient(Options(client_key=environ.get("GROWTHBOOK_CLIENT_KEY")))


def get_gb_client() -> GrowthBookClient:
    return gb_client


GBClientDep = Annotated[GrowthBookClient, Depends(get_gb_client)]


@asynccontextmanager
async def lifespan(app: FastAPI) -> Generator:
    # FastAPI doesn't support dependancies in lifespans, so we fetch it manually
    client = app.dependency_overrides.get(get_gb_client, get_gb_client)()
    await client.initialize()
    yield
    await client.close()


app = FastAPI(lifespan=lifespan)


@app.post("/evaluate_feature")
async def evaluate_feature(
    feature_request: FeatureRequest, gb_client: GBClientDep,
) -> FeatureResult:
    context = UserContext(attributes=feature_request.user_attributes)
    result = await gb_client.eval_feature(feature_request.feature_key, context)
    return FeatureResult.model_validate(result.to_dict())
