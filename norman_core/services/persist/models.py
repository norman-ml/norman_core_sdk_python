from typing import Optional

from norman_objects.shared.models.model import Model
from norman_objects.shared.models.model_preview import ModelPreview
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.requests.get_models_request import GetModelsRequest
from norman_objects.shared.security.sensitive import Sensitive
from norman_utils_external.singleton import Singleton
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class Models(metaclass=Singleton):
    """
    Provides coroutine-based methods for managing model records in the
    Norman persistence service.

    The `Models` class allows retrieving, creating, upgrading, replacing,
    activating, and deleting model entries stored in the Norman system.
    """

    def __init__(self) -> None:
        self._http_client = HttpClient()
    
    async def get_models(self, token: Sensitive[str], constraint: Optional[QueryConstraints] = None) -> dict[str, Model]:
        """
        **Coroutine**

        Retrieve model records that match the provided filtering constraints.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***request*** (`Optional[GetModelsRequest]`) —
          Optional request object specifying filters and pagination.
          If not provided, defaults to fetching all completed (`finished_models=True`) models.

          **Fields:**
          - **constraints** (`Optional[QueryConstraints]`) — Query filter rules.
          - **finished_models** (`bool`) — Whether to include only completed models.
          - **include_archived** (`Optional[bool]`) — Include archived models if `True`.
          - **limit / offset** (`Optional[int]`) — Pagination parameters.

        **Response Structure**

        - ***response*** (`dict[str, Model]`) —
          Dictionary mapping model IDs to corresponding `Model` objects.

          **Each `Model` includes:**
          - **id** (`str`) — Model identifier.
          - **name** (`str`) — Model name.
          - **version_label** (`str`) — Version or label (e.g., `"v1.0"`).
          - **description** (`str`) — Model description.
          - **created_at / updated_at** (`datetime`) — Timestamps for creation and last modification.

        **Example Usage:**
        ```python
        models_service = Models()
        models = await models_service.get_models(token=my_token)
        for model_id, model in models.items():
            print(f"{model.name} ({model.version_label})")
        ```
        """
        json = constraint.model_dump(mode="json")
        response = await self._http_client.post("persist/models/get", token, json=json)
        return TypeAdapter(dict[str, Model]).validate_python(response)

    
    async def create_models(self, token: Sensitive[str], models: list[Model]) -> dict[str, Model]:
        """
        **Coroutine**

        Create one or more new model records.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***models*** (`List[Model]`) —
          List of `Model` objects to be created.

          **Each `Model` includes:**
          - **name** (`str`) — Model name.
          - **version_label** (`str`) — Version or tag.
          - **short_description** (`str`) — Brief model summary.
          - **long_description** (`str`) — Detailed description.
          - **inputs / outputs** (`List[SignatureConfig]`) — Model I/O definitions.
          - **assets** (`List[AssetConfig]`) — Associated files and weights.

        **Response Structure**

        - ***response*** (`dict[str, Model]`) —
          Mapping of newly created model IDs to their corresponding model objects.

        **Example Usage:**
        ```python
        new_model = Model(name="text_reverser", version_label="v1.0")
        created = await Models().create_models(token=my_token, models=[new_model])
        print("Created model IDs:", list(created.keys()))
        ```
        """
        json = None
        if models is not None:
            json = TypeAdapter(list[Model]).dump_python(models, mode="json")

        response = await self._http_client.post("persist/models/", token, json=json)
        return TypeAdapter(list[Model]).validate_python(response)

    
    async def upgrade_models(self, token: Sensitive[str], models: list[Model]) -> dict[str, Model]:
        """
        **Coroutine**

        Upgrade existing models by creating new version entries.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***models*** (`List[Model]`) —
          List of existing model objects to be upgraded.
          Each upgraded model will receive a new version entry in the database.

        **Response Structure**

        - ***response*** (`dict[str, Model]`) —
          Dictionary mapping new version IDs to upgraded model objects.
        """
        json = None
        if models is not None:
            json = TypeAdapter(list[Model]).dump_python(models, mode="json")

        response = await self._http_client.post("persist/models/version", token, json=json)
        return TypeAdapter(list[Model]).validate_python(response)

    
    async def replace_models(self, token: Sensitive[str], models: list[Model]) -> dict[str, Model]:
        """
        **Coroutine**

        Replace existing models with updated definitions.

        This operation overwrites model metadata in bulk and should
        be used cautiously, as it may alter existing configurations.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***models*** (`List[Model]`) —
          List of model objects that should replace existing entries.

        **Response Structure**

        - ***response*** (`dict[str, Model]`) —
          Dictionary mapping updated model IDs to their new definitions.
        """
        json = None
        if models is not None:
            json = TypeAdapter(list[Model]).dump_python(models, mode="json")

        response = await self._http_client.patch("persist/models/", token, json=json)
        return TypeAdapter(list[Model]).validate_python(response)

    
    async def set_active_model(self, token: Sensitive[str], model_previews: list[ModelPreview]) -> list[ModelPreview]:
        """
        **Coroutine**

        Set one or more model versions as active.

        This method updates model metadata to mark specific model
        versions as active in the system.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***model_previews*** (`List[ModelPreview]`) —
          List of model previews to be marked as active.

          **Each `ModelPreview` includes:**
          - **id** (`str`) — Model preview identifier.
          - **model_id** (`str`) — ID of the associated model.
          - **version_label** (`str`) — Version label to set active.

        **Response Structure**

        - ***response*** (`List[ModelPreview]`) —
          List of updated `ModelPreview` objects now marked as active.
        """
        json = None
        if model_previews is not None:
            json = TypeAdapter(list[ModelPreview]).dump_python(model_previews, mode="json")

        response = await self._http_client.patch("persist/models/version", token, json=json)
        return TypeAdapter(list[ModelPreview]).validate_python(response)

    
    async def delete_models(self, token: Sensitive[str], constraints: QueryConstraints) -> int:
        """
        **Coroutine**

        Delete one or more model records that match the provided constraints.

        **Parameters**

        - ***token*** (`Sensitive[str]`) —
          Authentication token authorizing the request.

        - ***constraints*** (`QueryConstraints`) —
          Query constraints defining which models to delete.
          Supports filters like model name, ID, or status.

          **Example Fields:**
          - `filters` (`dict`) — Field-value filters for model attributes.
          - `limit` (`Optional[int]`) — Maximum number of models to delete.

        **Response Structure**

        - ***response*** (`int`) —
          Number of affected model records.
        """
        json = constraints.model_dump()

        affected_entities_count: int = await self._http_client.delete("persist/models/", token, json=json)
        return affected_entities_count
