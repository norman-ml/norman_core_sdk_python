from norman_utils_external.singleton import Singleton

from norman_core.services.authenticate.accounts import Accounts
from norman_core.services.authenticate.login import Login
from norman_core.services.authenticate.register import Register
from norman_core.services.authenticate.signup import Signup


class Authenticate(metaclass=Singleton):
    def __init__(self):
        self.accounts = Accounts()
        self.login = Login()
        self.register = Register()
        self.signup = Signup()


__all__ = ["Authenticate"]
