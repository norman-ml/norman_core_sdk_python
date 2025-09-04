from norman_objects.shared.accounts.account import Account
from norman_objects.shared.authorization.account_merge_request import AccountMergeRequest
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from pydantic import TypeAdapter

from norman_core.utils.api_client import ApiClient


class Accounts:
    @staticmethod
    async def get_accounts(api_client: ApiClient, token: Sensitive[str], constraints: QueryConstraints = None):
        response = await api_client.post("persist/accounts/get", token, json=constraints.model_dump(mode="json") if constraints else None)
        return TypeAdapter(list[Account]).validate_python(response)

    @staticmethod
    async def create_accounts(api_client: ApiClient, token: Sensitive[str], accounts: list[Account]):
        response = await api_client.post("persist/accounts", token, json=TypeAdapter(list[Account]).dump_python(accounts, mode="json"))
        return TypeAdapter(list[Account]).validate_python(response)

    @staticmethod
    async def replace_accounts(api_client: ApiClient, token: Sensitive[str], accounts: list[Account]):
        response = await api_client.put("persist/accounts", token, json=TypeAdapter(list[Account]).dump_python(accounts, mode="json"))
        return TypeAdapter(list[Account]).validate_python(response)

    @staticmethod
    async def update_accounts(api_client: ApiClient, token: Sensitive[str], account: Account.UpdateSchema, constraints: QueryConstraints = None):
        response = await api_client.patch(
            "persist/accounts",
            token,
            json=account.dump_python(mode="json"),
            params=constraints.dump_python(mode="json") if constraints else None
        )
        return TypeAdapter(list[Account]).validate_python(response)

    @staticmethod
    async def delete_account(api_client: ApiClient, token: Sensitive[str], constraints: QueryConstraints):
        response: int = await api_client.delete("persist/accounts", token, json=constraints.model_dump(mode="json"))
        return response

    @staticmethod
    async def merge_accounts(api_client: ApiClient, token: Sensitive[str], merge_request: AccountMergeRequest):
        response = await api_client.post("persist/account/merge", token, json=merge_request.model_dump(mode="json"))
        return Account.model_validate(response)

    @staticmethod
    async def does_account_exist(api_client: ApiClient, token: Sensitive[str], account_id: str):
        response: bool = await api_client.get(f"persist/exists/{account_id}", token)
        return response

    @staticmethod
    async def is_account_registered(api_client: ApiClient, token: Sensitive[str], account_id: str):
        response: bool = await api_client.get(f"persist/registered/{account_id}", token)
        return response
