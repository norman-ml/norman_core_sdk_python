import io
import os
import warnings
from pathlib import Path
from typing import cast, Final, Optional

import aiofiles
import pytest
from norman_objects.services.file_pull.requests.input_download_request import InputDownloadRequest
from norman_objects.services.file_push.checksum.checksum_request import ChecksumRequest
from norman_objects.services.file_push.pairing.socket_input_pairing_request import SocketInputPairingRequest
from norman_objects.shared.inputs.input_source import InputSource
from norman_objects.shared.inputs.invocation_input import InvocationInput
from norman_objects.shared.invocations.invocation import Invocation
from norman_objects.shared.models.model import Model
from norman_objects.shared.outputs.invocation_output import InvocationOutput
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.requests.get_models_request import GetModelsRequest
from norman_objects.shared.security.sensitive import Sensitive
from norman_objects.shared.signatures.model_signature import ModelSignature
from xxhash import xxh3_64

from norman_core.clients.http_client import HttpClient
from norman_core.clients.socket_client import SocketClient
from norman_core.services.file_pull.file_pull import FilePull
from norman_core.services.file_push.file_push import FilePush
from norman_core.services.persist import Persist
from norman_core.services.retrieve.retrieve import Retrieve
from tests.test_utils import get_flags_loop, http_client_logged_in

TEXT_INPUT: Final = "Hello World!"
TEXT_INPUT_LINK = "https://httpbin.org/base64/SGVsbG8gV29ybGQh" # returns "Hello World!"

image_input = "./tests/samples/model_logos/Delphi_logo.jpg"
mirror_image_input = "./tests/samples/model_logos/Delphi_logo_mirror.jpg"

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
    for model in models.values():
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


    input_signature = model.inputs[0]

    inputs = {
        input_signature.id: InputSource.Primitive
    }

    invocation = build_invocation_json(model, login_response.account.id, inputs)

    response = await Persist.invocations.create_invocations(http_client, login_response.access_token, [invocation])

    assert len(response) == 1
    _globals["invocation"] = response[0]

@pytest.mark.asyncio
async def test_upload_inputs(http_client_logged_in):
    http_client, login_response = http_client_logged_in

    invocation = _globals["invocation"]
    if invocation is None:
        warnings.warn("No invocation found")
        return

    await upload_inputs(http_client, login_response.account.id, login_response.access_token, invocation)

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

    get_models_request = GetModelsRequest(
        constraints=None,
        finished_models=True
    )
    models = await Persist.models.get_models(http_client, login_response.access_token, get_models_request)
    for model in models.values():
        if (
                len(model.inputs) == 1 and
                model.inputs[0].parameters[0].parameter_name == "image"
        ):
            break
    else:
        warnings.warn("No model with input 'image' found")
        _globals["invocation"] = None
        return

    input_signature = model.inputs[0]

    inputs = {
        input_signature.id: InputSource.File
    }

    invocation = build_invocation_json(model, login_response.account.id, inputs)

    response = await Persist.invocations.create_invocations(http_client, login_response.access_token, [invocation])

    assert len(response) == 1
    _globals["invocation"] = response[0]

@pytest.mark.asyncio
async def test_upload_image_inputs(http_client_logged_in):
    http_client, login_response = http_client_logged_in

    invocation = _globals["invocation"]
    if invocation is None:
        warnings.warn("No invocation found")
        return

    await upload_inputs(http_client, login_response.account.id, login_response.access_token, invocation, file_path=image_input)

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


def build_invocation_json(model: Model, account_id: str, inputs: dict[str, InputSource]):
    invocation_inputs: list[InvocationInput] = []
    for input_signature in model.inputs:
        invocation_input = build_invocation_input(input_signature, account_id, inputs[input_signature.id])
        invocation_inputs.append(invocation_input)

    invocation_outputs = [build_invocation_output(output_signature, account_id) for output_signature in model.outputs]

    return Invocation(
        account_id=account_id,
        model_id=model.id,
        inputs=invocation_inputs,
        outputs=invocation_outputs
    )

def build_invocation_input(input_signature: ModelSignature, account_id: str, input_source: InputSource):
    invocation_input = InvocationInput(
        account_id=account_id,
        model_id=input_signature.model_id,
        signature_id=input_signature.id,
        input_source=input_source,
    )

    return invocation_input

def build_invocation_output(output_signature: ModelSignature, account_id: str):
    return InvocationOutput(
        account_id=account_id,
        model_id=output_signature.model_id,
        signature_id=output_signature.id,
    )

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

async def upload_inputs(
        http_client: HttpClient,
        account_id: str,
        token: Sensitive[str],
        invocation: Invocation,
        file_path: str = None,
    ):
    for input_signature in invocation.inputs:
        if input_signature.input_source == InputSource.Link:
            download_request = InputDownloadRequest(
                account_id=account_id,
                model_id=input_signature.model_id,
                signature_id=input_signature.signature_id,
                invocation_id=invocation.id,
                input_id=input_signature.id,
                links=[TEXT_INPUT_LINK]
            )
            await FilePull.submit_input_links(http_client, token, download_request)
        else:
            if input_signature.input_source == InputSource.Primitive:
                file_stream = io.BytesIO()
                file_stream.write(TEXT_INPUT.encode("utf-8"))
                file_stream.seek(0)
                file_size = file_stream.getbuffer().nbytes
            else:
                file_stream = await aiofiles.open(file_path, "rb")
                file_size = Path(file_path).stat().st_size

            input_pairing_request = SocketInputPairingRequest(
                invocation_id=invocation.id,
                input_id=invocation.inputs[0].id,
                account_id=account_id,
                model_id=invocation.model_id,
                file_size_in_bytes=file_size,
            )
            socket_info = await FilePush.allocate_socket_for_input(http_client, token, input_pairing_request)

            file_checksum = await SocketClient.write_and_digest(socket_info, file_stream)
            if input_signature.input_source == InputSource.File:
                await file_stream.close()
            checksum_request = ChecksumRequest(
                checksum=file_checksum,
                pairing_id=socket_info.pairing_id
            )
            await FilePush.complete_file_transfer(http_client, token, checksum_request)
