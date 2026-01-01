from norman_utils_external.singleton import Singleton

from norman_core.services.authenticate.accounts import Accounts
from norman_core.services.authenticate.factors import Factors
from norman_core.services.authenticate.jwks import JWKS
from norman_core.services.authenticate.login import Login
from norman_core.services.authenticate.logout import Logout
from norman_core.services.authenticate.register import Register
from norman_core.services.authenticate.signup import Signup


class Authenticate(metaclass=Singleton):
    def __init__(self) -> None:
        self.accounts = Accounts()
        self.factors = Factors()
        self.jwks = JWKS()
        self.login = Login()
        self.logout = Logout()
        self.register = Register()
        self.signup = Signup()


__all__ = ["Authenticate"]
