import warnings
from typing import cast, Final, Optional

import aiofiles
import pytest
from norman_objects.services.invoke.invocation_config import InvocationConfig
from norman_objects.shared.invocations.invocation import Invocation
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.requests.get_models_request import GetModelsRequest
from norman_objects.shared.security.sensitive import Sensitive
from xxhash import xxh3_64

from norman_core.services.invoke.invoke import Invoke
from norman_core.services.persist import Persist
from norman_core.services.retrieve.retrieve import Retrieve
from norman_core.utils.api_client import HttpClient
from tests.test_utils import get_flags_loop, http_client_logged_in

TEXT_INPUT: Final = "Hello, world!"
image_input = "./tests/samples/model_logos/Delphi_logo.jpg"
mirror_image_input = "./tests/samples/model_logos/Delphi_logo_mirror.jpg"

avremy_account_id = "23845703660070374099865734459398242515"

_globals: Final = {
    "invocation": cast(Optional[Invocation], None),
}

@pytest.mark.asyncio
async def test_invoke_text(http_client_logged_in):
    http_client, login_response = http_client_logged_in

    get_models_request = GetModelsRequest(
        constraints=None,
        finished_models=True
    )
    models = await Persist.models.get_models(http_client, login_response.access_token, get_models_request)
    for model in models:
        if (
            len(model.inputs) == 1 and
            "test_model_" in model.name and
            model.inputs[0].parameters[0].parameter_name == "raw_text"
        ):
            break
    else:
        warnings.warn("No model with input 'raw_text' found")
        _globals["invocation"] = None
        return

    invocation_config = InvocationConfig(
        account_id=login_response.account.id,
        model_id=model.id,
        model_name=model.name,
        model_primitives = {},
        model_links = {},
        model_file_names = [],
    )

    input_signature = model.inputs[0]
    invocation_config.model_primitives[input_signature.id] = TEXT_INPUT

    response = await Invoke.invoke_model(http_client, login_response.access_token, invocation_config)

    assert isinstance(response, Invocation)
    _globals["invocation"] = response

@pytest.mark.asyncio
async def test_invocation_flags(http_client_logged_in):
    http_client, login_response = http_client_logged_in

    invocation = _globals["invocation"]
    if invocation is None:
        warnings.warn("No invocation found")
        return

    async def get_invocation_flags():
        invocation_constraints = QueryConstraints.equals("Invocation_Flags", "Entity_ID", invocation.id)
        results = await Persist.invocation_flags.get_invocation_status_flags(http_client, login_response.access_token, invocation_constraints)
        return {
            "Invocation": results[invocation.id]
        }

    all_finished, _ =  await get_flags_loop(get_invocation_flags, 1)

    assert all_finished

@pytest.mark.asyncio
async def test_get_text_results(http_client_logged_in):
    http_client, login_response = http_client_logged_in
    invocation = _globals["invocation"]
    if invocation is None:
        warnings.warn("No invocation found")
        return

    _, response_stream = await get_invoke_results(http_client, login_response.access_token, invocation)
    response = bytearray()
    async for chunk in response_stream:
        response.extend(chunk)

    assert response.decode("utf-8") == TEXT_INPUT[::-1]

@pytest.mark.asyncio
async def test_invoke_image(http_client_logged_in):
    http_client, login_response = http_client_logged_in
    _globals["invocation"] = None

    models = await Persist.models.get_models(http_client, login_response.access_token)

    for model in models:
        if (
                len(model.inputs) == 1 and
                model.inputs[0].parameters[0].parameter_name == "image"
        ):
            break
    else:
        warnings.warn("No model with input 'image' found")
        return
    invocation_config = InvocationConfig(
        account_id=login_response.account.id,
        model_id=model.id,
        model_name=model.name,
        model_primitives = {},
        model_links = {},
        model_file_names = [],
    )

    signature_id = model.inputs[0].id
    invocation_config.model_file_names.append(signature_id)

    file_stream = await aiofiles.open(image_input, "rb")
    response = await Invoke.invoke_model(http_client, login_response.access_token, invocation_config, {
        signature_id: file_stream,
    })
    await file_stream.close()

    assert isinstance(response, Invocation)
    _globals["invocation"] = response

test_invocation_flags_image = test_invocation_flags

@pytest.mark.asyncio
async def test_get_image_results(http_client_logged_in):
    http_client, login_response = http_client_logged_in
    invocation = _globals["invocation"]
    if invocation is None:
        warnings.warn("No invocation found")
        return

    hash_stream = xxh3_64()

    _, response_stream_handler = await get_invoke_results(http_client, login_response.access_token, invocation)
    async for chunk in response_stream_handler:
        hash_stream.update(chunk)

    async with aiofiles.open(mirror_image_input, "rb") as file:
        hash_expected = xxh3_64(await file.read()).digest()
        assert hash_expected == hash_stream.digest()

async def get_invoke_results(http_client: HttpClient, token: Sensitive[str], invocation: Invocation):
    response = await Retrieve.get_invocation_output(
        http_client,
        token,
        invocation.account_id,
        invocation.model_id,
        invocation.id,
        invocation.outputs[0].id
    )
    return response
