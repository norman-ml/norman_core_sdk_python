from norman_objects.shared.notifications.notification import Notification
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from pydantic import TypeAdapter

from norman_core.utils.api_client import ApiClient


class Notifications:
    @staticmethod
    async def get_notifications(api_client: ApiClient, token: Sensitive[str], constraints: QueryConstraints = None):
        response = await api_client.post("persist/notifications/get", token, json=constraints.model_dump(mode="json") if constraints else None)
        return TypeAdapter(list[Notification]).validate_python(response)
