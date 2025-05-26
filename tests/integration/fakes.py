from growthbook import FeatureResult, GrowthBook, Options, UserContext

FEATURES = {
    "prototype-feature": {
        "defaultValue": "A",
        "rules": [
            {
                "id": "test-ruleid",
                "coverage": 1,
                "hashAttribute": "whatsapp_id",
                "seed": "6a2bc50c-1d6a-406f-a8df-8f270ec6d08c",
                "hashVersion": 2,
                "variations": ["A", "B", "C"],
                "weights": [0.3334, 0.3333, 0.3333],
                "key": "test-experiment",
                "meta": [
                    {"key": "A", "name": "Group A"},
                    {"key": "B", "name": "Group B"},
                    {"key": "C", "name": "Group C"},
                ],
                "phase": "0",
                "name": "Prototype experiment",
            },
        ],
    },
}


class FakeGrowthBookClient:
    """Fake GrowthBook async client that calculates results, but doesn't make a network
    call to fetch feature configuration. Instead relies on hardcoded FEATURES.

    Only implements a subset of the functionality that we require.
    """

    def __init__(self, options: Options) -> None:
        self.options = options
        self.initialized = False
        self.closed = False

    async def initialize(self) -> None:
        self.initialized = True

    async def close(self) -> None:
        self.closed = True

    async def eval_feature(
        self, feature_key: str, user_context: UserContext
    ) -> FeatureResult:
        # The sync client supports supplying features and not requiring network
        # access, but the async client doesn't, so we use the sync client here
        # to do the calculations
        client = GrowthBook(features=FEATURES, attributes=user_context.attributes)
        return client.evalFeature(key=feature_key)
