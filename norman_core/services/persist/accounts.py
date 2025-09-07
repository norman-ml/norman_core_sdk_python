from typing import Optional

from norman_objects.shared.accounts.account import Account
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from pydantic import TypeAdapter

from norman_core.utils.api_client import ApiClient


class Accounts:
    @staticmethod
    async def get_accounts(api_client: ApiClient, token: Sensitive[str], constraints: Optional[QueryConstraints] = None):
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")

        response = await api_client.post("persist/accounts/get", token, json=json)
        return TypeAdapter(list[Account]).validate_python(response)

    @staticmethod
    async def create_accounts(api_client: ApiClient, token: Sensitive[str], accounts: list[Account]):
        json = TypeAdapter(list[Account]).dump_python(accounts, mode="json")

        response = await api_client.post("persist/accounts", token, json=json)
        return TypeAdapter(list[Account]).validate_python(response)

    @staticmethod
    async def replace_accounts(api_client: ApiClient, token: Sensitive[str], accounts: list[Account]):
        json = None
        if accounts is not None:
            json = TypeAdapter(list[Account]).dump_python(accounts, mode="json")

        modified_entity_count: int = await api_client.put("persist/accounts", token, json=json)
        return modified_entity_count

    @staticmethod
    async def update_accounts(api_client: ApiClient, token: Sensitive[str], account: Account.UpdateSchema, constraints: Optional[QueryConstraints] = None):
        json = account.model_dump(mode="json")
        params = None
        if constraints is not None:
            params = constraints.model_dump(mode="json")

        affected_entities_count: int = await api_client.patch("persist/accounts", token, json=json, params=params)
        return affected_entities_count

    @staticmethod
    async def delete_account(api_client: ApiClient, token: Sensitive[str], constraints: QueryConstraints):
        json = constraints.model_dump(mode="json")

        affected_entities_count: int = await api_client.delete("persist/accounts", token, json=json)
        return affected_entities_count
