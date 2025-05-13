from pydantic import BaseModel
from typing import Any


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
    ruleId: str | None
    experiment: Experiment | None
