import dataclasses
from typing import Any
from typing import Dict
from typing import Optional
from typing import Set

import pytest


ADD_GRAND_QUERY = """
    insert into
        roles.grands (
            login,
            role_id,
            is_fired
        )
    values
        ($1, $2, $3)
    returning
        id
    ;
"""


@pytest.fixture(name='add_grand')
def _add_grand(web_context):
    async def _wrapper(
            login: str, role_id: int, is_fired: Optional[bool] = None,
    ) -> int:
        record = await web_context.pg.primary.fetchrow(
            ADD_GRAND_QUERY, login, role_id, is_fired,
        )
        return record['id']

    return _wrapper


@dataclasses.dataclass(frozen=True)
class Grand:
    login: str
    role_id: int

    def __eq__(self, other):
        if not isinstance(other, Grand):
            return dataclasses.asdict(self) == other
        return dataclasses.asdict(self) == dataclasses.asdict(other)


@pytest.fixture(name='get_grands')
def _get_grands(web_context):
    async def _do_it() -> Set[Grand]:
        records = await web_context.pg.primary.fetch(
            """
            SELECT login, role_id FROM roles.grands WHERE NOT is_deleted
            """,
        )
        return {Grand(**x) for x in records}

    return _do_it


@pytest.fixture(name='grands_retrieve')
def _grands_retrieve(requests_post):
    async def _wrapper(
            filters: Optional[dict] = None,
            limit: Optional[int] = None,
            cursor: Optional[dict] = None,
    ):
        body: Dict[str, Any] = {}
        if filters is not None:
            body['filters'] = filters
        if limit is not None:
            body['limit'] = limit
        if cursor is not None:
            body['cursor'] = cursor
        return await requests_post('/grands/v1/retrieve/', body)

    return _wrapper
