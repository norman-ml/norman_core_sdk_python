from norman_core.services.authenticate.accounts import Accounts
from norman_core.services.authenticate.login import Login
from norman_core.services.authenticate.register import Register
from norman_core.services.authenticate.signup import Signup


class Authenticate:
    accounts = Accounts
    login = Login
    register = Register
    signup = Signup

__all__ = ['Authenticate']
