import asyncio
from pprint import pprint

from norman_objects.services.authenticate.login.name_password_login_request import NamePasswordLoginRequest
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.requests.get_models_request import GetModelsRequest
from norman_objects.shared.security.sensitive import Sensitive
from norman_objects.shared.signatures.model_signature import ModelSignature

from norman_core import ApiClient
from norman_core.services.authenticate.login import Login
from norman_core.services.persist.model_bases import ModelBases
from norman_core.services.persist.models import Models


async def login(api_client: ApiClient):
    login_request = NamePasswordLoginRequest(
        name="avremy",
        password=Sensitive("Avremy123!"),
    )
    response = await Login.login_password_name(api_client, login_request)
    return response.account, response.access_token


def print_input_data(input_data: list[ModelSignature]):
    pprint(input_data)


async def get_models(api_client: ApiClient, token: Sensitive[str]):
    print("Getting models...")
    models = await Models.get_models(api_client, token)
    for model in models:
        print(f"Model: {model.name}")
        print(f"Version: {model.version_label}")
        print_input_data(model.inputs)

    return models


async def get_bases(api_client: ApiClient, token: Sensitive[str], account_id: str):
    get_models_request = GetModelsRequest(
        constraints=QueryConstraints.equals("Model_Bases", "Account_ID", account_id),
        finished_models=True
    )
    response = await ModelBases.get_model_bases(api_client, token, get_models_request)
    print(
        f"Found {len(response)} bases for account {account_id}:"
    )
    for base in response:
        pprint(base.model_dump())

    return response

async def main():
    api_client = ApiClient()
    account, token = await login(api_client)

    print(f"Account ID: {account.id}")
    print(f"Access Token: {token}")

    # await get_models(api_client, token)

    bases = await get_bases(api_client, token, account.id)
    bi_versional = [base for base in bases if len(base.model_previews) == 2]

    print(f"Bi-versional models: {len(bi_versional)}")


    selected_previews = []

    for base in bi_versional:
        p1, p2 = base.model_previews
        if p1.active:
            selected_previews.append(p2)
        else:
            selected_previews.append(p1)


    response = await Models.set_active_model(api_client, token, selected_previews)
    print("Version change response:", response)
    await get_models(api_client, token)

    await api_client.close()

asyncio.run(main())