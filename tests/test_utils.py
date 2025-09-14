import asyncio
from time import time
from typing import Callable, Awaitable

import pytest_asyncio
from norman_objects.services.authenticate.login.name_password_login_request import NamePasswordLoginRequest
from norman_objects.shared.status_flags.status_flag import StatusFlag
from norman_objects.shared.status_flags.status_flag_value import StatusFlagValue

from norman_core.clients.http_client import HttpClient
from norman_core.services.authenticate.login import Login
from norman_core.services.authenticate.signup import Signup
from tests.test_config import username, password

GetFlagsFunction = Callable[[], Awaitable[dict[str, list[StatusFlag]]]]


@pytest_asyncio.fixture
async def http_client():
    client = HttpClient()
    async with client:
        yield client

@pytest_asyncio.fixture
async def http_client_guest():
    client = HttpClient()
    async with client:
        response = await Signup.signup_default(client)
        yield client, response

@pytest_asyncio.fixture
async def http_client_logged_in():
    client = HttpClient()
    async with client:
        login_request = NamePasswordLoginRequest(name=username, password=password)
        response = await Login.login_password_name(client, login_request)
        yield client, response

async def get_flags_loop(get_flags_func: GetFlagsFunction, interval: float = 5.0):
    start_time = time()
    print()
    while True:
        flags = await get_flags_func()
        flag_values = list(flags.values())
        for key in flags:
            _print_flags(key, flags[key])
        _print_elapsed_time(start_time)

        concat_flags = [flag for row in flag_values for flag in row]
        any_failed = any(
            flag.flag_value == StatusFlagValue.Error
            for flag in concat_flags
        )
        all_finished = all(
            flag.flag_value == StatusFlagValue.Finished
            for flag in concat_flags
        ) if len(concat_flags) > 0 else False

        if any_failed or all_finished:
            break
        else:
            await asyncio.sleep(interval)

        print(f"\033[{len(concat_flags) + 1}A", end="", flush=True)

    return all_finished, any_failed

def _print_flags(group: str, flags: list[StatusFlag]):
    for flag in flags:
        if flag.flag_value == StatusFlagValue.Error:
            color = "\033[31m"
        elif flag.flag_value == StatusFlagValue.Finished:
            color = "\033[32m"
        else:
            color = "\033[34m"
        reset = "\033[0m"
        print(
            f"StatusFlag<{group}>"
            f"({flag.flag_name}, {color}{flag.flag_value.name}{reset})"
            f"\033[K"
        )

def _print_elapsed_time(start_time: float):
    elapsed_time = int(time() - start_time)
    minutes = str(elapsed_time // 60).rjust(2, "0")
    seconds = str(elapsed_time % 60).rjust(2, "0")

    print(f"Elapsed time: {minutes}:{seconds} minutes")

def upload_progress_indicator(asset_file_size: int):
    bytes_uploaded = 0
    full_size = asset_file_size + 16
    print()
    try:
        while True:
            chunk_len = yield
            bytes_uploaded += chunk_len
            percentage = bytes_uploaded / full_size * 100
            finished = "█" * int(percentage // 5)
            awaiting = "░" * int(20 - (percentage // 5))
            print(f"\rUploaded {str(bytes_uploaded).rjust(len(str(full_size)))}/{full_size} bytes :: {finished}{awaiting} ", end="", flush=True)
    except GeneratorExit:
        print()

def get_name_with_time(name: str):
    time_stamp = time()
    return f"{name}_{int(time_stamp)}"
