# Norman Core SDK Overview

The Norman Core SDK is a low-level foundational library that powers all Norman services and underlies the higher-level Norman SDK.

For most use cases, we strongly recommend using the high-level Norman SDK, which provides a simpler, more ergonomic interface for interacting with Norman services and abstracts away internal implementation details.

The Core SDK is intended only for users who require fine-grained control over how operations are executed. It exposes low-level utilities used internally by the Norman platform, including HTTP communication, file streaming, socket-level encryption, and direct access to stored model data.

The following example demonstrates a typical Core SDK workflow: manually authenticating to exchange an API key for an access token, applying specific query constraints, and extracting version metadata directly from the persistence layer.

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
    client = HttpClient()
    login_service = Login()
    model_service = Models()

    async with client:
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

Comprehensive documentation is available on our website:
https://sdk.norman-ai.com/api/core

