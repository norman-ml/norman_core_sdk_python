from norman_utils_external.singleton import Singleton

from norman_core.services.persist.invocations import Invocations
from norman_core.services.persist.model_bases import ModelBases
from norman_core.services.persist.models import Models
from norman_core.services.persist.notifications import Notifications
from norman_core.services.persist.status_flags import StatusFlags


class Persist(metaclass=Singleton):
    def __init__(self):
        self.invocations = Invocations()
        self.model_bases = ModelBases()
        self.models = Models()
        self.notifications = Notifications()
        self.status_flags = StatusFlags()

__all__ = ["Persist"]
