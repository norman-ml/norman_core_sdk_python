from typing import Optional

from norman_objects.shared.accounts.account import Account
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from norman_utils_external.singleton import Singleton
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class Accounts(metaclass=Singleton):
    """
    Provides high-level CRUD operations for managing accounts
    through the Norman authentication service.

    This class communicates with the `authenticate/accounts` endpoints
    and exposes coroutine methods for creating, retrieving, updating,
    and replacing accounts.
    """

    def __init__(self) -> None:
        self._http_client = HttpClient()

    async def get_accounts(
        self,
        token: Sensitive[str],
        constraints: Optional[QueryConstraints] = None
    ) -> dict[str, Account]:
        """
        **Coroutine**

        Retrieve existing accounts that match the provided query constraints.

        **Parameters**

        - ***token*** (`Sensitive[str]`) — Authentication token authorizing the request.
        - ***constraints*** (`Optional[QueryConstraints]`) — Optional filtering and pagination constraints for narrowing down results.


        **Response Structure**

        - ***response*** (`dict[str, Account]`) —
          Dictionary mapping account IDs to their corresponding `Account` objects.

        **Example Usage:**
        ```python
        accounts_service = Accounts()
        accounts = await accounts_service.get_accounts(token=my_token)
        for account_id, account in accounts.items():
            print(account_id, account.name)
        ```
        """
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")

        response = await self._http_client.post("authenticate/accounts/get", token, json=json)
        return TypeAdapter(dict[str, Account]).validate_python(response)

    async def create_accounts(
        self,
        token: Sensitive[str],
        accounts: list[Account]
    ) -> list[Account]:
        """
        **Coroutine**

        Create one or more new accounts.

        **Parameters**

        - ***token*** (`Sensitive[str]`) — Authentication token authorizing the request.

        - ***accounts*** (`List[Account]`) — List of `Account` objects to be created.

        **Response Structure**

        - ***response*** (`List[Account]`) — List of newly created accounts, validated against the `Account` schema.

        **Example Usage:**
        ```python
        new_accounts = [Account(name="Alice"), Account(name="Bob")]
        accounts_service = Accounts()
        created = await accounts_service.create_accounts(token=my_token, accounts=new_accounts)
        ```
        """
        json = TypeAdapter(list[Account]).dump_python(accounts, mode="json")

        response = await self._http_client.post("authenticate/accounts", token, json=json)
        return TypeAdapter(list[Account]).validate_python(response)

    async def replace_accounts(
        self,
        token: Sensitive[str],
        accounts: list[Account]
    ) -> int:
        """
        **Coroutine**

        Replace all existing accounts with a new list.

        This operation overwrites existing records and is typically used for
        synchronization or bulk migration scenarios.

        **Parameters**

        - ***token*** (`Sensitive[str]`) — Authentication token authorizing the request.

        - ***accounts*** (`List[Account]`) — New list of accounts that should replace the existing ones.

        **Response Structure**

        - ***response*** (`int`) —
          The number of entities modified or replaced.

        **Example Usage:**
        ```python
        accounts_service = Accounts()
        replaced_count = await accounts_service.replace_accounts(token=my_token, accounts=new_accounts)
        print(f"Replaced {replaced_count} accounts.")
        ```
        """
        json = None
        if accounts is not None:
            json = TypeAdapter(list[Account]).dump_python(accounts, mode="json")

        modified_entity_count: int = await self._http_client.put("authenticate/accounts", token, json=json)
        return modified_entity_count

    async def update_accounts(
        self,
        token: Sensitive[str],
        account: Account.UpdateSchema,
        constraints: Optional[QueryConstraints] = None
    ) -> int:
        """
        **Coroutine**

        Update one or more existing accounts that match given query constraints.

        **Parameters**

        - ***token*** (`Sensitive[str]`) — Authentication token authorizing the request.
        - ***account*** (`Account.UpdateSchema`) — Partial account update schema defining fields to modify.

        - ***constraints*** (`Optional[QueryConstraints]`) — Conditions for selecting which accounts to update.

        **Response Structure**

        - ***response*** (`int`) — Number of accounts affected by the update operation.

        **Example Usage:**
        ```python
        update_schema = Account.UpdateSchema(name="Updated Name")
        constraints = QueryConstraints(filters={"role": "user"})
        accounts_service = Accounts()
        count = await accounts_service.update_accounts(token=my_token, account=update_schema, constraints=constraints)
        print(f"Updated {count} accounts.")
        ```
        """
        parsed_constraints = None
        if constraints is not None:
            parsed_constraints = constraints.model_dump(mode="json")

        json = {
            "account": account.model_dump(mode="json"),
            "constraints": parsed_constraints
        }

        affected_entities_count: int = await self._http_client.patch("authenticate/accounts", token, json=json)
        return affected_entities_count
