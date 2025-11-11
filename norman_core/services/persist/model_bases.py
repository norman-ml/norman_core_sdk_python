from typing import Optional

from norman_objects.shared.models.model_base import ModelBase
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from norman_utils_external.singleton import Singleton
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class ModelBases(metaclass=Singleton):
    """
    Provides coroutine-based access to retrieve model base definitions
    from the Norman persistence layer.

    The `ModelBases` class allows fetching metadata and configuration
    information about foundational models (pretrained, versioned, or
    template models) available in the system.
    """

    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def get_model_bases(self, token: Sensitive[str], constraint: Optional[QueryConstraints] = None) -> dict[str, ModelBase]:
        """
        **Coroutine**

        Retrieve all model bases that match the provided filtering constraints.

        If no request is provided, defaults to fetching all completed (`finished_models=True`)
        model bases.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***request*** (`Optional[GetModelsRequest]`) —
          Optional filtering and pagination request specifying which models to retrieve.

          **Fields:**
          - **constraints** (`Optional[QueryConstraints]`) — Optional filtering and sorting rules.
          - **finished_models** (`bool`) — Whether to include only completed models.
          - **include_archived** (`Optional[bool]`) — Whether to include archived models.
          - **limit / offset** (`Optional[int]`) — Pagination parameters.

        **Response Structure**

        - ***response*** (`dict[str, ModelBase]`) —
          Dictionary mapping model base IDs to corresponding `ModelBase` objects.

          **Each `ModelBase` includes:**
          - **id** (`str`) — Unique identifier of the model base.
          - **name** (`str`) — Human-readable model base name.
          - **version** (`str`) — Version label or tag (e.g., `"v1.0"`).
          - **description** (`Optional[str]`) — Textual description of the model.
          - **created_at** (`datetime`) — Timestamp when the model was created.

        **Example Usage:**
        ```python
        model_bases_service = ModelBases()
        models = await model_bases_service.get_model_bases(token=my_token)
        for model_id, base in models.items():
            print(f"{base.name} (v{base.version})")
        ```
        """
        json = constraint.model_dump(mode="json")
        response = await self._http_client.post("persist/models/bases/get", token, json=json)
        return TypeAdapter(dict[str, ModelBase]).validate_python(response)
