# GrowthBook API
Exposes the growthbook client as an HTTP API, to allow us to interact with it where we cannot run a client

This uses the async version of the GrowthBook client, and [FastAPI](https://fastapi.tiangolo.com/) for the API.

## Running the service
This project uses [uv](https://docs.astral.sh/uv/) to manage dependancies. After [installing uv](https://docs.astral.sh/uv/installation), you can run a development server using the following command:

```bash
uv run fastapi dev src/growthbook_api/main.py
```

## Development
This project uses ruff for linting:
```bash
uv run ruff check
```
ruff for formatting:
```bash
uv run ruff format
```
mypy for type checking:
```bash
uv run mypy .
```
and pytest for the test runner:
```bash
uv run pytest
```

## API
The API is documented and available at the `/docs/` endpoint of the service. It just passes through the request details to the client. For more information on those fields, please see the [growthbook python client documentation](https://docs.growthbook.io/lib/python) and the [growthbook documentation](https://docs.growthbook.io/). The currently implemented endpoints are:
- `evaluate_feature`. This corresponds to the `eval_feature` method of the GrowthBook client. It takes in the `feature_key` and `user_attributes` parameters, and returns the `value`, `source`, `on`/`off`, `ruleId` and `experiment`.
For example, the following request body:
```json
{
    "feature_key": "my_feature",
    "user_attributes": {
        "email": "user@example.com"
    }
}
```
translates to the following Python code:
```python
context = UserContext(attributes={"email": "user@example.com"})
return await gb_client.eval_feature("my_feature", context)
```
and can give a response body like:
```json
{
    "experiment": {
        "key": "test-experiment",
    },
    "off": false,
    "on": true,
    "ruleId": "test-ruleid",
    "source": "experiment",
        "value": "B",
}
```

## Authentication
This relies on the client to manage authentication keys and send the key to the service on every request. The key is sent as a header named `Client-Token`.

## Multi-tenant
This service is able to serve multiple clients, each with their own client token. Just pass a different token in the header, and it will fetch the configuration for that client. It will keep all the clients in memory and in SSE mode so that they will get updates to the configuration and respond immediately. Only the first request for each token will have a delay while it fetches the configuration from growthbook.
