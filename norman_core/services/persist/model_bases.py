from typing import Optional

from norman_objects.shared.models.model_base import ModelBase
from norman_objects.shared.requests.get_models_request import GetModelsRequest
from norman_objects.shared.security.sensitive import Sensitive
from pydantic import TypeAdapter

from norman_utils_external.singleton import Singleton
from norman_core.clients.http_client import HttpClient


class ModelBases(metaclass=Singleton):
    def __init__(self):
        self._http_client = HttpClient()

    async def get_model_bases(self, token: Sensitive[str], request: Optional[GetModelsRequest] = None) -> dict[str, ModelBase]:
        if request is None:
            request = GetModelsRequest(constraints=None, finished_models=True)
        json = request.model_dump(mode="json")

        response = await self._http_client.post("persist/models/bases/get", token, json=json)
        return TypeAdapter(dict[str, ModelBase]).validate_python(response)
