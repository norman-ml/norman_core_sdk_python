from typing import cast, Optional

import pytest
from norman_objects.services.authenticate.login.name_password_login_request import NamePasswordLoginRequest
from norman_objects.services.authenticate.signup.signup_password_request import SignupPasswordRequest
from norman_objects.shared.accounts.account import Account
from norman_objects.shared.security.sensitive import Sensitive

from norman_core.services.authenticate import Authenticate
from tests.test_config import password
from tests.test_utils import http_client, get_name_with_time

_globals = {
    "account": cast(Optional[Account], None),
    "access_token": cast(Optional[Sensitive[str]], None),
    "id_token": cast(Optional[Sensitive[str]], None),
}

@pytest.mark.asyncio
async def test_signup_default(http_client):
    response = await Authenticate.signup.signup_default(http_client)
    assert response.account is not None
    assert response.access_token is not None
    assert response.id_token is not None

@pytest.mark.asyncio
async def test_signup_user(http_client):
    t_username = get_name_with_time("username")
    request = SignupPasswordRequest(name=t_username, password=password)
    response = await Authenticate.signup.signup_with_password(http_client, request)
    _globals["account"] = response

@pytest.mark.asyncio
async def test_login(http_client):
    account: Account = _globals["account"]
    assert isinstance(account, Account), "not an account"

    login_request = NamePasswordLoginRequest(name=account.name, password=password)
    response = await Authenticate.login.login_password_name(http_client, login_request)

    assert response.account is not None
    assert response.access_token is not None
    assert response.id_token is not None

    _globals["account"] = response.account
    _globals["access_token"] = response.access_token
    _globals["id_token"] = response.id_token
