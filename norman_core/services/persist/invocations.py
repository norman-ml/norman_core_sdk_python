from typing import Optional

from norman_objects.shared.invocations.invocation import Invocation
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from pydantic import TypeAdapter

from norman_utils_external.singleton import Singleton
from norman_core.clients.http_client import HttpClient


class Invocations(metaclass=Singleton):
    """
    Provides coroutine-based methods for managing invocation records within
    the Norman persistence service.

    The `Invocations` class allows creating new invocation entries, retrieving
    existing ones, fetching invocation history, and generating invocations
    based on model names and execution counts.
    """

    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def get_invocations(
        self,
        token: Sensitive[str],
        constraints: Optional[QueryConstraints] = None
    ) -> dict[str, Invocation]:
        """
        **Coroutine**

        Retrieve invocation records that match the provided query constraints.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***constraints*** (`Optional[QueryConstraints]`) —
          Optional query object defining filters and pagination.

        **Response Structure**

        - ***response*** (`dict[str, Invocation]`) —
          Dictionary mapping invocation IDs to their corresponding `Invocation` objects.
        """
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")
        response = await self._http_client.post("persist/invocations/get", token, json=json)
        return TypeAdapter(dict[str, Invocation]).validate_python(response)

    async def create_invocations(
        self,
        token: Sensitive[str],
        invocations: list[Invocation]
    ) -> list[Invocation]:
        """
        **Coroutine**

        Create one or more new invocation records.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***invocations*** (`List[Invocation]`) —
          List of `Invocation` objects representing executions to persist.

        **Response Structure**

        - ***response*** (`List[Invocation]`) —
          List of successfully created invocation objects returned from the server.
        """
        json = TypeAdapter(list[Invocation]).dump_python(invocations, mode="json")
        response = await self._http_client.post("persist/invocations", token, json=json)
        return TypeAdapter(list[Invocation]).validate_python(response)

    async def create_invocations_by_model_names(
        self,
        token: Sensitive[str],
        model_name_counter: dict[str, int]
    ) -> list[Invocation]:
        """
        **Coroutine**

        Create invocation records in bulk, using model names and execution counts.

        This method generates multiple invocation records for each specified model name,
        based on the provided count mapping.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***model_name_counter*** (`dict[str, int]`) —
          Mapping of model names to the number of invocations to create.

        **Response Structure**

        - ***response*** (`List[Invocation]`) —
          List of newly created invocation records corresponding to the counts provided.
        """
        response = await self._http_client.post("persist/invocations/by-name", token, json=model_name_counter)
        return TypeAdapter(list[Invocation]).validate_python(response)

    async def get_invocation_history(
        self,
        token: Sensitive[str],
        constraints: Optional[QueryConstraints] = None
    ) -> dict[str, Invocation]:
        """
        **Coroutine**

        Retrieve historical invocation records based on the provided query constraints.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***constraints*** (`Optional[QueryConstraints]`) —
          Optional query object for filtering historical invocations.

        **Response Structure**

        - ***response*** (`dict[str, Invocation]`) —
          Dictionary mapping invocation IDs to corresponding historical invocation objects.
        """
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")
        response = await self._http_client.post("persist/invocation/history/get", token, json=json)
        return TypeAdapter(dict[str, Invocation]).validate_python(response)
