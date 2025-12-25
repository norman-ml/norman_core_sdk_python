# Norman Core SDK Overview

The Norman Core SDK is the low-level foundational library that powers Norman inter-service communication and underlies the higher-level Norman SDK.

For most use cases, we recommend using the high-level Norman SDK, which provides a simple interface with Norman and abstracts the underlying implementation details.

The Core SDK is recommended for users who require fine-grained control over operation execution. It provides low-level utilities for http and socket communication, as well as fully mapped direct access to every route exposed by the Norman backend.

The following example demonstrates a typical workflow which requires use of the Core SDK: manually authenticating to exchange an API key for an access token, applying specific query constraints, and extracting version metadata directly from the persistence layer.

```python
from norman_core.clients.http_client import HttpClient
from norman_core.services.authenticate import Login
from norman_core.services.persist import Models

from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from norman_objects.services.authenticate.login.api_key_login_request import ApiKeyLoginRequest

API_KEY = Sensitive("<your_api_key>")
MODEL_ID = "<your_model_id>"

async def main():
    # Initialize Core Services
    http_client = HttpClient()
    login_service = Login()
    model_service = Models()

    async with http_client:
        # Authenticate to generate an access token
        login_request = ApiKeyLoginRequest(api_key=API_KEY)
        login_response = await login_service.login_with_key(login_request)
        access_token = login_response.access_token

        # Define constraints to fetch the specific model
        constraints = QueryConstraints.equals("Models", "ID", MODEL_ID)

        # Retrieve model metadata
        model_previews = await model_service.get_model_previews(access_token, constraints)
        model_preview = model_previews.get(MODEL_ID)

        if model_preview is None:
            raise ValueError(f"Model with ID {MODEL_ID} not found.")

        # Map version labels to their current build status
        model_versions_build_status = {version.label: version.build_status for version in model_preview.versions}
        print(model_versions_build_status)
```

For the full reference and detailed instructions, please visit our Core SDK documentation at https://sdk.norman-ai.com/api/core.