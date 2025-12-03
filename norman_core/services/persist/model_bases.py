from typing import Optional

from norman_objects.shared.models.model_base import ModelBase
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from norman_utils_external.singleton import Singleton
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class ModelBases(metaclass=Singleton):
    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def get_model_bases(self, token: Sensitive[str], constraint: Optional[QueryConstraints] = None) -> dict[str, ModelBase]:
        json = constraint.model_dump(mode="json")
        response = await self._http_client.post("persist/models/bases/get", token, json=json)
        return TypeAdapter(dict[str, ModelBase]).validate_python(response)
