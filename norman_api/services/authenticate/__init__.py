from norman_utils.singleton import Singleton

from norman_api.services.authenticate.accounts import Accounts
from norman_api.services.authenticate.capacity import Capacity
from norman_api.services.authenticate.factors import Factors
from norman_api.services.authenticate.jwks import JWKS
from norman_api.services.authenticate.login import Login
from norman_api.services.authenticate.logout import Logout
from norman_api.services.authenticate.register import Register
from norman_api.services.authenticate.signup import Signup


class Authenticate(metaclass=Singleton):
    def __init__(self) -> None:
        self.accounts = Accounts()
        self.capacity = Capacity()
        self.factors = Factors()
        self.jwks = JWKS()
        self.login = Login()
        self.logout = Logout()
        self.register = Register()
        self.signup = Signup()


__all__ = ["Authenticate"]
