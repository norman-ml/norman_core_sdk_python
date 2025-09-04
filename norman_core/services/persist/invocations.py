from norman_objects.shared.invocations.invocation import Invocation
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from pydantic import TypeAdapter

from norman_core.utils.api_client import ApiClient


class Invocations:
    @staticmethod
    async def get_invocations(api_client: ApiClient, token: Sensitive[str], constraints: QueryConstraints = None):
        response = await api_client.post("persist/invocations/get", token, json=constraints.model_dump(mode="json") if constraints else None)
        return response

    @staticmethod
    async def create_invocations(api_client: ApiClient, token: Sensitive[str], invocations: list[Invocation]):
        response = await api_client.post("persist/invocations", token, json=TypeAdapter(list[Invocation]).dump_python(invocations, mode="json"))
        return response

    @staticmethod
    async def get_invocation_history(api_client: ApiClient, token: Sensitive[str], constraints: QueryConstraints = None):
        response = await api_client.post("persist/invocation/history/get", token, json=constraints.model_dump(mode="json") if constraints else None)
        return response
