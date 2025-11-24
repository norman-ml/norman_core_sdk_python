from typing import Optional

from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from norman_objects.shared.status_flags.status_flag import StatusFlag
from norman_utils_external.singleton import Singleton
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class StatusFlags(metaclass=Singleton):
    """
    Provides coroutine-based access to retrieve status flags stored
    in the Norman persistence service.

    The `StatusFlags` class allows querying operational flags, health indicators,
    or runtime markers for various Norman entities such as models,
    invocations, or services.
    """

    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def get_status_flags(
        self,
        token: Sensitive[str],
        constraints: Optional[QueryConstraints] = None
    ) -> dict[str, list[StatusFlag]]:
        """
        **Coroutine**

        Retrieve status flags matching the specified query constraints.

        This method fetches one or more collections of status flags from the
        persistence layer, grouped by their associated entity identifiers.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***constraints*** (`Optional[QueryConstraints]`) —
          Optional query object for filtering or pagination.

        **Response Structure**

        - ***response*** (`dict[str, list[StatusFlag]]`) —
          Dictionary mapping entity IDs to a list of `StatusFlag` objects.
        """
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")

        response = await self._http_client.post("/persist/flags/get", token, json=json)
        return TypeAdapter(dict[str, list[StatusFlag]]).validate_python(response)
