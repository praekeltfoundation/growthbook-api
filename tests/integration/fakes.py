from growthbook import GrowthBook

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
            }
        ],
    }
}


class FakeGrowthBookClient:
    def __init__(self):
        self.initialized = False
        self.closed = False

    async def initialize(self):
        self.initialized = True

    async def close(self):
        self.closed = True

    async def eval_feature(self, feature_key, user_context):
        # The sync client supports supplying features and not requiring network
        # access, but the async client doesn't, so we use the sync client here
        # to do the calculations
        client = GrowthBook(features=FEATURES, attributes=user_context.attributes)
        return client.evalFeature(key=feature_key)
