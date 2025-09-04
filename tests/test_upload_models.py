import asyncio
import random
from pathlib import Path
from time import time
from typing import Optional, Final, cast
from typing_extensions import Literal

import aiofiles
import pytest
from norman_objects.services.file_push.checksum.checksum_request import ChecksumRequest
from norman_objects.services.file_push.pairing.socket_asset_pairing_request import SocketAssetPairingRequest
from norman_objects.shared.accounts.account import Account
from norman_objects.shared.models.http_request_type import HttpRequestType
from norman_objects.shared.models.model import Model
from norman_objects.shared.models.model_asset import ModelAsset
from norman_objects.shared.models.model_hosting_location import ModelHostingLocation
from norman_objects.shared.models.model_type import ModelType
from norman_objects.shared.models.output_format import OutputFormat
from norman_objects.shared.parameters.data_domain import DataDomain
from norman_objects.shared.parameters.model_param import ModelParam
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.requests.get_models_request import GetModelsRequest
from norman_objects.shared.security.sensitive import Sensitive
from norman_objects.shared.signatures.http_location import HttpLocation
from norman_objects.shared.signatures.model_signature import ModelSignature
from norman_objects.shared.signatures.receive_format import ReceiveFormat
from norman_objects.shared.signatures.signature_type import SignatureType
from norman_utils_external.streaming_utils import StreamingUtils, AsyncBufferedReader
from norman_utils_external.uuid_utils import UUIDUtils
from xxhash import xxh3_64

from norman_core._app_config import AppConfig
from norman_core.services.file_push.file_push import FilePush
from norman_core.services.persist.model_bases import ModelBases
from norman_core.services.persist.model_flags import ModelFlags
from norman_core.services.persist.models import Models
from norman_core.utils.api_client import ApiClient
from tests.test_utils import api_client_logged_in, get_flags_loop, upload_progress_indicator

email = "avremy.back@norman-ai.com"
password = "Avremy123!"
account_id = "23844127049894141074602308225775386835"

text_model_path = "./tests/samples/model_files/text_qa_model.pt"
image_model_path = "./tests/samples/model_files/image_qa_model.pt"

_globals: Final = {
    "model": cast(Optional[Model], None),
}

@pytest.mark.asyncio
async def test_upload_model(api_client_logged_in):
    api_client, login_response = api_client_logged_in

    model = create_model(login_response.account, ModelType.Pytorch_jit)

    model.assets.append(create_model_asset(model, "Logo"))
    model.assets.append(create_model_asset(model, "File"))
    model.inputs.append(
        create_model_signature(
            model,
            SignatureType.Input,
            data_domain=DataDomain.Text,
            data_encoding="utf8",
            http_location=HttpLocation.Body,
            receive_format=ReceiveFormat.Primitive,
            param_name="raw_text"
        )
    )
    model.outputs.append(
        create_model_signature(
            model,
            SignatureType.Output,
            data_domain=DataDomain.Text,
            data_encoding="utf8",
            http_location=HttpLocation.Body,
            receive_format=ReceiveFormat.Primitive,
            param_name="reverse_text"
        )
    )

    created_model = await Models.create_models(api_client, login_response.access_token, [model])

    assert isinstance(created_model, dict) and isinstance(created_model[model.id], Model)

    _globals["model"] = created_model[model.id]

@pytest.mark.asyncio
async def test_upload_model_logo(api_client_logged_in):
    api_client, login_response = api_client_logged_in

    model = _globals["model"]
    assert isinstance(model, Model)

    await upload_model_asset(api_client, login_response.access_token, model, "Logo")

@pytest.mark.asyncio
async def test_upload_model_file(api_client_logged_in):
    api_client, login_response = api_client_logged_in

    model = _globals["model"]
    assert isinstance(model, Model)

    await upload_model_asset(api_client, login_response.access_token, model, "File", Path(text_model_path))

@pytest.mark.slow
@pytest.mark.asyncio
async def test_model_flags(api_client_logged_in):
    api_client, login_response = api_client_logged_in

    model = _globals["model"]
    assert isinstance(model, Model)

    logo_asset = next(asset for asset in model.assets if asset.asset_name == "Logo")
    file_asset = next(asset for asset in model.assets if asset.asset_name == "File")

    async def get_model_flags():
        model_flag_constraints = QueryConstraints.equals("Model_Flags", "Entity_ID", model.id)
        asset_flag_constraints = QueryConstraints.includes("Asset_Flags", "Entity_ID", [file_asset.id, logo_asset.id])

        model_flag_task = ModelFlags.get_model_status_flags(api_client, login_response.access_token, model_flag_constraints)
        asset_flag_task = ModelFlags.get_asset_status_flags(api_client, login_response.access_token, asset_flag_constraints)

        results = await asyncio.gather(model_flag_task, asset_flag_task)
        logo_flags = results[1][logo_asset.id]
        file_flags = results[1][file_asset.id]

        return {
            "Model": results[0][model.id],
            "Logo": logo_flags,
            "File": file_flags,
        }

    all_finished, _ = await get_flags_loop(get_model_flags)


    assert all_finished, "Some flags didn't finish"

@pytest.mark.upgrade
@pytest.mark.asyncio
async def test_upgrade_model(api_client_logged_in):
    api_client, login_response = api_client_logged_in

    model = _globals["model"]
    assert isinstance(model, Model)

    model.id = UUIDUtils.bytes_to_str_id(UUIDUtils.optimized_unique_id())
    model.name = f"test_model_upgrade_{int(time())}"
    model.version_label = "v2.0"

    model.assets = [
        create_model_asset(model, "Logo"),
        create_model_asset(model, "File")
    ]

    model.inputs = [
        create_model_signature(
            model,
            SignatureType.Input,
        )
    ]

    model.outputs = [
        create_model_signature(
            model,
            SignatureType.Output,
            param_name="mirror_image",
        )
    ]

    created_model = await Models.upgrade_models(api_client, login_response.access_token, [model])
    assert isinstance(created_model, dict) and isinstance(created_model[model.id], Model)
    _globals["model"] = created_model[model.id]

@pytest.mark.upgrade
@pytest.mark.asyncio
async def test_upload_model_logo_upgrade(api_client_logged_in):
    await test_upload_model_logo(api_client_logged_in)

@pytest.mark.upgrade
@pytest.mark.asyncio
async def test_upload_model_file_upgrade(api_client_logged_in):
    api_client, login_response = api_client_logged_in

    model = _globals["model"]
    assert isinstance(model, Model)

    await upload_model_asset(api_client, login_response.access_token, model, "File", Path(image_model_path))

@pytest.mark.upgrade
@pytest.mark.slow
@pytest.mark.asyncio
async def test_model_flags_upgrade(api_client_logged_in):
    await test_model_flags(api_client_logged_in)

# marked as slow because it requires model images to be fully finished
@pytest.mark.upgrade
@pytest.mark.slow
@pytest.mark.asyncio
async def test_set_active_model(api_client_logged_in):
    api_client, login_response = api_client_logged_in

    base_id = _globals["model"].model_base_id

    get_models_request = GetModelsRequest(
        constraints=QueryConstraints.equals("Model_Bases", "ID", base_id),
        finished_models=True
    )
    model_bases = await ModelBases.get_model_bases(api_client, login_response.access_token, get_models_request)
    assert len(model_bases) == 1, "Expected model base"

    previews = model_bases[0].model_previews
    assert len(previews) == 2, "Expected two model versions"
    v1_preview = next(preview for preview in previews if preview.version_label == "v1.0")

    await Models.set_active_model(api_client, login_response.access_token, [v1_preview])

def create_model(account: Account, model_type: ModelType) -> Model:
    model =  Model(
        id=UUIDUtils.bytes_to_str_id(UUIDUtils.optimized_unique_id()),
        account_id=account.id,
        model_base_id=UUIDUtils.bytes_to_str_id(UUIDUtils.optimized_unique_id()),
        version_label="v1.0",
        active=True,
        name=f"test_model_{model_type.name.lower()}_{int(time())}",
        url="https://test.url",
        request_type=HttpRequestType.Post,
        model_type=model_type,
        hosting_location=ModelHostingLocation.Internal if model_type == ModelType.Pytorch_jit else ModelHostingLocation.External,
        output_format=OutputFormat.Json,
        short_description="test_short_description",
        long_description="test_long_description",
        inputs=[],
        outputs=[],
        http_headers={},
        assets=[],
    )

    return model

def create_model_asset(model: Model, asset_name: Literal["Logo", "File"]) -> ModelAsset:
    asset = ModelAsset(
        id=UUIDUtils.bytes_to_str_id(UUIDUtils.optimized_unique_id()),
        account_id=model.account_id,
        model_id=model.id,
        asset_name=asset_name
    )
    return asset

def create_model_signature(
        model: Model,
        signature_type: SignatureType,
        /, *,
        data_domain: DataDomain = DataDomain.Image,
        data_encoding: str = "png",
        receive_format: ReceiveFormat = ReceiveFormat.File,
        http_location: HttpLocation = HttpLocation.Body,
        hidden: bool = False,
        param_name: str = None,
) -> ModelSignature:
    signature = ModelSignature(
        id=UUIDUtils.bytes_to_str_id(UUIDUtils.optimized_unique_id()),
        model_id=model.id,
        signature_type=signature_type,
        data_domain=data_domain,
        data_encoding=data_encoding,
        receive_format=receive_format,
        http_location=http_location,
        hidden=hidden,
        display_title=signature_type.value,
        parameters=[]
    )
    param = ModelParam(
        id=UUIDUtils.bytes_to_str_id(UUIDUtils.optimized_unique_id()),
        model_id=model.id,
        signature_id=signature.id,
        data_domain=data_domain,
        data_encoding=data_encoding,
        parameter_name=param_name or "image"
    )

    signature.parameters.append(param)
    return signature

async def upload_model_asset(api_client: ApiClient, token: Sensitive[str], model: Model, asset_name: Literal["Logo", "File"], asset_path: Path = None):
    asset_path = get_random_model_logo() if asset_path is None else asset_path
    asset_file_size = asset_path.stat().st_size
    asset_stream = await aiofiles.open(asset_path, "rb")

    asset = next(asset for asset in model.assets if asset.asset_name == asset_name)

    pairing_request = SocketAssetPairingRequest(
        model_id=asset.model_id,
        asset_id=asset.id,
        account_id=model.account_id,
        file_size_in_bytes=asset_file_size
    )

    pairing_response = await FilePush.allocate_socket_for_asset(api_client, token, pairing_request)

    hash_stream = xxh3_64()
    body_stream = StreamingUtils.process_read_stream(asset_stream, hash_stream.update, AppConfig.io.chunk_size, False)

    progress_indicator = upload_progress_indicator(asset_file_size)
    next(progress_indicator)

    async for chunk in FilePush.write_file(pairing_response, body_stream):
        progress_indicator.send(len(chunk))

    progress_indicator.close()

    await asset_stream.close()
    file_checksum = hash_stream.hexdigest()

    checksum_request = ChecksumRequest(
        checksum=file_checksum,
        pairing_id=pairing_response.pairing_id
    )

    await FilePush.complete_file_transfer(api_client, token, checksum_request)

def get_random_model_logo() -> Path:
    root_path = Path("./tests/samples/model_logos/")
    return random.choice(list(root_path.iterdir()))
