import pytest
from norman_objects.shared.models.model import Model
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.requests.get_models_request import GetModelsRequest

from norman_core.services.persist.models import Models
from tests.test_utils import http_client_logged_in


@pytest.mark.asyncio
async def test_get_models(http_client_logged_in):
    http_client, login_response = http_client_logged_in
    response = await Models.get_models(http_client, login_response.access_token)
    assert len(response) == 0 or isinstance(response[0], Model)

@pytest.mark.asyncio
async def test_get_account_models(http_client_logged_in):
    http_client, login_response = http_client_logged_in

    get_models_request = GetModelsRequest(
        constraints=QueryConstraints.equals("Model_Bases", "Account_ID", login_response.account.id),
        finished_models=True
    )
    response = await Models.get_models(http_client, login_response.access_token, get_models_request)
    assert len(response) != 0, f"No models found for {response.a.name}"

    assert response[0].account_id == login_response.account.id, "Model account ID does not match"
