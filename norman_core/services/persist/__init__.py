from norman_core.services.persist.invocations import Invocations
from norman_core.services.persist.model_bases import ModelBases
from norman_core.services.persist.models import Models
from norman_core.services.persist.notifications import Notifications
from norman_core.services.persist.status_flags import StatusFlags


class Persist:
    invocations = Invocations
    model_bases = ModelBases
    models = Models
    notifications = Notifications
    status_flags = StatusFlags


__all__ = ["Persist"]
