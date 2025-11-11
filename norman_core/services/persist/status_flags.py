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

          **Example Fields:**
          - `filters` (`dict`) — Field-value filters (e.g., `"entity_type": "model"`).
          - `limit` (`int`) — Maximum number of results to return.
          - `offset` (`int`) — Number of items to skip for pagination.
          - `sort_by` (`str`) — Field used for sorting (e.g., `"updated_at"`).
          - `descending` (`bool`) — Whether to sort results in descending order.

        **Response Structure**

        - ***response*** (`dict[str, list[StatusFlag]]`) —
          Dictionary mapping entity IDs to a list of `StatusFlag` objects.

          **Each `StatusFlag` includes:**
          - **id** (`str`) — Unique identifier for the flag.
          - **entity_id** (`str`) — ID of the entity the flag belongs to.
          - **type** (`str`) — Category or type of the flag (e.g., `"health"`, `"operation"`).
          - **value** (`bool`) — Current flag state or value.
          - **created_at / updated_at** (`datetime`) — Timestamps for flag creation and last update.

        **Example Usage:**
        ```python
        status_flags_service = StatusFlags()

        # Retrieve all status flags for models
        constraints = QueryConstraints(filters={"entity_type": "model"})
        flags = await status_flags_service.get_status_flags(token=my_token, constraints=constraints)

        for entity_id, entity_flags in flags.items():
            print(f"Entity: {entity_id}")
            for flag in entity_flags:
                print(f"  - {flag.type}: {flag.value}")
        ```
        """
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")

        response = await self._http_client.post("/persist/flags/get", token, json=json)
        return TypeAdapter(dict[str, list[StatusFlag]]).validate_python(response)
