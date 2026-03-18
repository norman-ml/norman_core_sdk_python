from typing import Optional

from norman_objects.shared.provisioning.provisioned_instance import ProvisionedInstance
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from norman_utils.singleton import Singleton
from pydantic import TypeAdapter

from norman_api.clients.http_client import HttpClient


class ProvisionedInstances(metaclass=Singleton):
    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def get_provisioned_instances(self, token: Sensitive[str], constraints: Optional[QueryConstraints] = None) -> list[ProvisionedInstance]:
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")

        response = await self._http_client.post("persist/instances/provisioned/get", token, json=json)
        return TypeAdapter(list[ProvisionedInstance]).validate_python(response)

    async def create_provisioned_instances(self, token: Sensitive[str], instances: list[ProvisionedInstance]) -> list[ProvisionedInstance]:
        json = TypeAdapter(list[ProvisionedInstance]).dump_python(instances, mode="json")

        response = await self._http_client.post("persist/instances/provisioned", token, json=json)
        return TypeAdapter(list[ProvisionedInstance]).validate_python(response)

    async def replace_provisioned_instances(self, token: Sensitive[str], instances: list[ProvisionedInstance]) -> list[ProvisionedInstance]:
        json = TypeAdapter(list[ProvisionedInstance]).dump_python(instances, mode="json")

        response = await self._http_client.put("persist/instances/provisioned", token, json=json)
        return TypeAdapter(list[ProvisionedInstance]).validate_python(response)