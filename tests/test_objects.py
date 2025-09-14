import asyncio
import json
import random
from datetime import datetime
from typing import Any

import pytest
from norman_objects.services.authenticate.signup.signup_password_request import SignupPasswordRequest
from norman_objects.shared.security.sensitive import Sensitive
from norman_objects.shared.status_flags.status_flag import StatusFlag
from norman_objects.shared.status_flags.status_flag_value import StatusFlagValue
from pydantic import BaseModel

from tests.test_utils import get_flags_loop, upload_progress_indicator


class SomeModel(BaseModel):
    data: int

class SensitiveCheck(BaseModel):
    string: Sensitive[str]
    integer: Sensitive[int]
    boolean: Sensitive[bool]
    lst: Sensitive[list[int]]
    dictionary : Sensitive[dict[str, Any]]
    inner: Sensitive[SomeModel]

ACCOUNT = "account"
PASSWORD = "password"
some_model = SomeModel(data=1)

def test_create_with_string():
    request = SignupPasswordRequest(name=ACCOUNT, password=PASSWORD)
    assert request.password.value() == PASSWORD

def test_create_with_sensitive():
    password = Sensitive(PASSWORD)
    request = SignupPasswordRequest(name=ACCOUNT, password=password)
    assert request.password.value() == PASSWORD

def test_sensitive():
    string = Sensitive("1")
    integer = Sensitive(1)
    boolean = Sensitive(True)
    lst = Sensitive(["1", "2"])
    dictionary = Sensitive({"1": "2"})
    inner = Sensitive(some_model)

    assert string.value() == "1"
    assert integer.value() == 1
    assert boolean.value() == True
    assert lst.value() == ["1", "2"]
    assert dictionary.value()["1"] == "2"
    assert inner.value().data == 1

    check = SensitiveCheck(string=string, integer=integer, boolean=boolean, lst=lst, dictionary=dictionary, inner=inner)

    assert check.string.value() == "1"
    assert check.integer.value() == 1
    assert check.boolean.value() == True
    assert check.dictionary.value()["1"] == "2"
    assert check.inner.value().data == 1

def test_sensitive_with_raw():
    string = "1"
    integer = 1
    boolean = True
    lst = ["1"]
    dictionary = {"1": 5}
    inner = {
        "data": 1
    }

    check = SensitiveCheck(string=string, integer=integer, boolean=boolean, lst=lst, dictionary=dictionary, inner=inner)

    assert check.string.value() == "1"
    assert check.integer.value() == 1
    assert check.boolean.value() == True
    assert check.dictionary.value()["1"] == 5
    assert check.inner.value().data == 1

def test_serialize():
    request = SignupPasswordRequest(name=ACCOUNT, password=PASSWORD)
    dump = request.model_dump()
    assert isinstance(dump["password"], Sensitive) and dump["password"].value() == PASSWORD

    dump_mode_json = request.model_dump(mode="json")
    assert dump_mode_json["password"] == PASSWORD

    dump_json = request.model_dump_json()
    assert isinstance(dump_json, str) and json.loads(dump_json)["password"] == PASSWORD

    a = SignupPasswordRequest(**dump)
    b = SignupPasswordRequest(**dump_mode_json)
    c = SignupPasswordRequest.model_validate_json(dump_json)
    assert a == b == c

@pytest.mark.asyncio
async def test_progress_indicator():
    p = upload_progress_indicator(84)
    next(p)
    for _ in range(100):
        p.send(1)
        await asyncio.sleep(.1)

@pytest.mark.asyncio
async def test_flag_print():
    flags = random_flag_getter()
    await get_flags_loop(random_flag_updater(flags), 2)

def random_flag_getter():
    flags = {
        "Invocation": [],
        "Model": [],
        "Logo": [],
        "File": []
    }
    flag_names = ["Input_Storage", "Function_Invocation", "Output_Storage", "File"]
    statuses = [StatusFlagValue.Not_Started, StatusFlagValue.Enqueued, StatusFlagValue.In_Progress, StatusFlagValue.Finished]
    for flag in flags:
        for _ in range(random.randint(0, 2)):
            flags[flag].append(StatusFlag(
                account_id="",
                update_time=datetime.now(),
                flag_name=random.choice(flag_names),
                flag_value=random.choice(statuses)
            ))
    return flags

def random_flag_updater(flags: dict[str, list[StatusFlag]]):
    statuses = [StatusFlagValue.Not_Started, StatusFlagValue.Enqueued, StatusFlagValue.In_Progress, StatusFlagValue.Finished]

    async def get_flags():
        await asyncio.sleep(0)
        for flag_list in flags.values():
            for flag in flag_list:
                min = statuses.index(flag.flag_value)
                flag.flag_value = random.choice(statuses[min:])
                if random.random() < 0.1:
                    flag.flag_value = StatusFlagValue.Error
        return flags
    return get_flags
