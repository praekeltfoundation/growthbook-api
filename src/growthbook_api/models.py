from typing import Any

from pydantic import BaseModel


class FeatureRequest(BaseModel):
    feature_key: str
    user_attributes: dict


class Experiment(BaseModel):
    key: str


class FeatureResult(BaseModel):
    value: Any
    source: str
    on: bool
    off: bool
    ruleId: str | None  # noqa: N815 - provided by parent API
    experiment: Experiment | None
