from norman_utils.singleton import Singleton

from norman_api.services.persist.capacity_usage import CapacityUsageService
from norman_api.services.persist.invocations import Invocations
from norman_api.services.persist.models import Models
from norman_api.services.persist.notifications import Notifications
from norman_api.services.persist.provisioned_instances import ProvisionedInstances
from norman_api.services.persist.status_flags import StatusFlags
from norman_api.services.persist.tags import Tags


class Persist(metaclass=Singleton):
    def __init__(self) -> None:
        self.capacity_usage = CapacityUsageService()
        self.invocations = Invocations()
        self.models = Models()
        self.notifications = Notifications()
        self.provisioned_instances = ProvisionedInstances()
        self.status_flags = StatusFlags()
        self.tags = Tags()

__all__ = ["Persist"]
