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

          **Example Fields:**
          - `limit` (`int`) — Maximum number of records to return.
          - `offset` (`int`) — Number of records to skip.
          - `filters` (`dict`) — Attribute-based filtering rules.

        **Response Structure**

        - ***response*** (`dict[str, Invocation]`) —
          Dictionary mapping invocation IDs to their corresponding `Invocation` objects.

        **Example Usage:**
        ```python
        invocations_service = Invocations()
        invocations = await invocations_service.get_invocations(token=my_token)
        for inv_id, inv in invocations.items():
            print(inv_id, inv.model_name)
        ```
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

          **Each invocation includes:**
          - **model_id** (`str`) — ID of the model executed.
          - **inputs** (`dict`) — Input data or references used in the execution.
          - **outputs** (`dict`) — Model outputs or references.
          - **status** (`str`) — Execution status (`"running"`, `"completed"`, etc.).
          - **start_time / end_time** (`datetime`) — Execution timing data.

        **Response Structure**

        - ***response*** (`List[Invocation]`) —
          List of successfully created invocation objects returned from the server.

        **Example Usage:**
        ```python
        inv = Invocation(model_id="model_123", status="completed")
        result = await Invocations().create_invocations(token=my_token, invocations=[inv])
        print(f"Created {len(result)} invocation record(s).")
        ```
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
          For example:
          ```python
          {"image_reverser_model": 3, "text_summary_model": 2}
          ```

        **Response Structure**

        - ***response*** (`List[Invocation]`) —
          List of newly created invocation records corresponding to the counts provided.

        **Example Usage:**
        ```python
        model_counts = {"text_reverser": 2, "image_captioner": 1}
        invocations = await Invocations().create_invocations_by_model_names(token=my_token, model_name_counter=model_counts)
        print("Created invocations:", [i.model_name for i in invocations])
        ```
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

          **Example Fields:**
          - `date_range` (`tuple[datetime, datetime]`) — Time window for fetching records.
          - `status` (`str`) — Filter by invocation status.
          - `model_name` (`str`) — Retrieve history for a specific model.

        **Response Structure**

        - ***response*** (`dict[str, Invocation]`) —
          Dictionary mapping invocation IDs to corresponding historical invocation objects.

        **Example Usage:**
        ```python
        history = await Invocations().get_invocation_history(token=my_token)
        ```
        """
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")
        response = await self._http_client.post("persist/invocation/history/get", token, json=json)
        return TypeAdapter(dict[str, Invocation]).validate_python(response)
