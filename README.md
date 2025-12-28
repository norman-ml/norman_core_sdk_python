# Norman Core SDK Overview

The Norman Core SDK is the low-level foundational library that powers Norman inter-service communication and underlies the higher-level Norman SDK.

For most use cases, we recommend using the high-level Norman SDK, which provides a simple interface with Norman and abstracts the underlying implementation details.

The Core SDK is recommended for users who require fine-grained control over operation execution. It provides low-level utilities for http and socket communication, as well as fully mapped direct access to every route exposed by the Norman backend.

The following example demonstrates a typical workflow which requires use of the Core SDK: manually authenticating to exchange an API key for an access token, applying specific query constraints, and extracting version metadata directly from the persistence layer.


## 1. Install the Norman Core SDK

To use the Norman Core SDK in Python, we need to install it using the **pip** package manager:
```bash
pip install norman-core
````


## 2. Signup and create an API key

Once we have the Core SDK set up, we need to sign up to Norman and create our first API key. 
To do so we initialize the Signup class and provide it with a username of our choice.

Notice that all API calls in the Core SDK must be within the context of an HTTPClient. 
This allows granular control over session management, 
and is more efficient than opening and closing new sessions for each call.

```python
import asyncio
from typing import Tuple

from norman_objects.services.authenticate.signup.signup_key_request import SignupKeyRequest
from norman_objects.services.authenticate.signup.signup_key_response import SignupKeyResponse
from norman_objects.shared.accounts.account import Account
from norman_objects.shared.security.sensitive import Sensitive

from norman_core.clients.http_client import HttpClient
from norman_core.services.authenticate import Signup


async def signup_to_norman() -> Tuple[Account, Sensitive[str]]:
    # Define communication services and helper classes
    http_client: HttpClient = HttpClient()
    signup_service: Signup = Signup()

    # Set your account name and create a signup request
    account_name: str = "WobblyWalrus1337"
    signup_request: SignupKeyRequest = SignupKeyRequest(name=account_name)

    # Signup to Norman with your signup request
    async with http_client:
        signup_response: SignupKeyResponse = await signup_service.signup_and_generate_key(signup_request=signup_request)

    # Retrieve your account and API key from the signup response
    account: Account = signup_response.account
    api_key: Sensitive[str] = Sensitive(signup_response.api_key)

    # Return the account and API key to the caller
    return account, api_key

signup_coroutine = signup_to_norman()
asyncio.run(signup_coroutine)
```


## 3. Login using the API key to obtain an access token

API keys are the credentials you use to authenticate with Norman. 
Keep them stored safely to prevent them from being misused or compromised. 
Now that we have an API key, we can use it to login to Norman and obtain an access token.

Access tokens are temporary scoped authorization claims that are used to perform actions in the Norman API.
In this example we initialize the Login class and provide it with the API key we generated.|

The login class then authenticates with the Norman backend, 
and provides an access token if the authentication was successful.

```python
import asyncio

from norman_objects.services.authenticate.login.api_key_login_request import ApiKeyLoginRequest
from norman_objects.services.authenticate.login.login_response import LoginResponse
from norman_objects.shared.security.sensitive import Sensitive

from norman_core.clients.http_client import HttpClient
from norman_core.services.authenticate import Login


async def get_access_token() -> Sensitive[str]:
    # Define communication services and helper classes
    http_client: HttpClient = HttpClient()
    login_service: Login = Login()

    # Set your api key and create a login request
    api_key: Sensitive[str] = Sensitive("<your_api_key>")
    login_request: ApiKeyLoginRequest = ApiKeyLoginRequest(api_key=api_key)

    # Login to Norman with your login request
    async with http_client:
        login_response: LoginResponse = await login_service.login_with_key(api_key_login_request=login_request)

    # Retrieve your access token from the login response
    access_token: Sensitive[str] = login_response.access_token

    # Return the access token to the caller
    return access_token

access_token_coroutine = get_access_token()
asyncio.run(access_token_coroutine)
```



## 4. Sample use case

The high-level Norman SDK is sufficient for most general use cases. It lets you run models, deploy models and manage your account, credentials, security and API keys. 

However, there are use cases in which you would need or prefer more granular control over your models.
In this sample code, we will programatically retrieve the configuration preview for a specific model, 
assumed to be previously created by our account, 
and check which versions of that model are active and deployed. 

These versions can then be used downstream to ensure we only invoke active and deployed versions.

```python
import asyncio
from typing import List

from norman_objects.shared.models.model_build_status import ModelBuildStatus
from norman_objects.shared.models.model_preview import ModelPreview
from norman_objects.shared.models.model_version_preview import ModelVersionPreview
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive

from norman_core.clients.http_client import HttpClient
from norman_core.services.persist import Models


async def get_model_build_status() -> List[ModelVersionPreview]:
    # Define communication services and helper classes
    http_client: HttpClient = HttpClient()
    model_service: Models = Models()

    # Set your access token and model id
    access_token: Sensitive[str] = Sensitive("<your_access_token>")
    model_id: str = "<your_model_id>"

    # Define constraints to fetch the configuration preview for the model you specified
    constraints: QueryConstraints = QueryConstraints.equals("Models", "ID", model_id)

    # Retrieve all configuration previews matching the constraints fron the Norman backend
    async with http_client:
        model_previews: dict[str, ModelPreview] = await model_service.get_model_previews(access_token, constraints)

    # Select the configuration preview for your chosen model
    model_preview: ModelPreview = model_previews[model_id]

    # Filter the active and complete versions of the model you chose
    active_model_versions: list[ModelVersionPreview] = [
        version
        for version in model_preview.versions
        if version.build_status == ModelBuildStatus.Completed
        and version.active
    ]

    # Return the model versions to the caller
    return active_model_versions


model_build_status_coroutine = get_model_build_status()
asyncio.run(model_build_status_coroutine)
```

## 5. Next steps

This guide covers a single representative workflow using the Norman Core SDK.
The Core SDK exposes many additional services and operations beyond the example shown here.

For the full reference and detailed instructions, please visit our documentation at https://sdk.norman-ai.com/api/core.