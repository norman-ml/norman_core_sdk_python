from typing import Optional

from norman_objects.shared.accounts.account import Account
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from norman_utils_external.singleton import Singleton
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class Accounts(metaclass=Singleton):
    def __init__(self):
        self._http_client = HttpClient()

    async def get_accounts(self, token: Sensitive[str], constraints: Optional[QueryConstraints] = None) -> dict[str, Account]:
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")

        response = await self._http_client.post("authenticate/accounts/get", token, json=json)
        return TypeAdapter(dict[str, Account]).validate_python(response)

    async def create_accounts(self, token: Sensitive[str], accounts: list[Account]) -> list[Account]:
        json = TypeAdapter(list[Account]).dump_python(accounts, mode="json")

        response = await self._http_client.post("authenticate/accounts", token, json=json)
        return TypeAdapter(list[Account]).validate_python(response)

    async def replace_accounts(self, token: Sensitive[str], accounts: list[Account]) -> int:
        json = None
        if accounts is not None:
            json = TypeAdapter(list[Account]).dump_python(accounts, mode="json")

        modified_entity_count: int = await self._http_client.put("authenticate/accounts", token, json=json)
        return modified_entity_count

    async def update_accounts(self, token: Sensitive[str], account: Account.UpdateSchema, constraints: Optional[QueryConstraints] = None) -> int:
        parsed_constraints = None
        if constraints is not None:
            parsed_constraints = constraints.model_dump(mode="json")

        json = {
            "account": account.model_dump(mode="json"),
            "constraints": parsed_constraints
        }

        affected_entities_count: int = await self._http_client.patch("authenticate/accounts", token, json=json)
        return affected_entities_count
