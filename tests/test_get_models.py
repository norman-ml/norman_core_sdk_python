import warnings

import pytest
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.requests.get_models_request import GetModelsRequest

from norman_core.services.persist import Persist
from tests.test_utils import http_client_logged_in


@pytest.mark.asyncio
async def test_get_models(http_client_logged_in):
    http_client, login_response = http_client_logged_in
    response = await Persist.models.get_models(http_client, login_response.access_token)
    if len(response) == 0:
        warnings.warn("No models found")


@pytest.mark.asyncio
async def test_get_account_models(http_client_logged_in):
    http_client, login_response = http_client_logged_in

    get_models_request = GetModelsRequest(
        constraints=QueryConstraints.equals("Model_Bases", "Account_ID", login_response.account.id),
        finished_models=True
    )

    response = await Persist.models.get_models(http_client, login_response.access_token, get_models_request)
    if len(response) == 0:
        warnings.warn(f"No models found for user: '{login_response.account.name}'")
        return

    assert all(model.account_id == login_response.account.id for model in response.values()), "Model account ID does not match"
