from typing import Optional

from norman_objects.shared.models.model_base import ModelBase
from norman_objects.shared.requests.get_models_request import GetModelsRequest
from norman_objects.shared.security.sensitive import Sensitive
from pydantic import TypeAdapter

from norman_core.utils.api_client import ApiClient


class ModelBases:
    @staticmethod
    async def get_model_bases(api_client: ApiClient, token: Sensitive[str], request: Optional[GetModelsRequest] = None):
        if request is None:
            request = GetModelsRequest(constraints=None, finished_models=True)
        json = request.model_dump(mode="json")

        response = await api_client.post("persist/models/bases/get", token, json=json)
        return TypeAdapter(list[ModelBase]).validate_python(response)
