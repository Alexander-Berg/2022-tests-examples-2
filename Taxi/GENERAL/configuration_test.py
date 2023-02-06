import dataclasses
from typing import List, Optional  # noqa: IS001

import asyncpg

from supportai_lib.utils import postgres


@dataclasses.dataclass
class ConfigurationTest:
    id: int  # pylint: disable=invalid-name
    task_id: str
    request_text: str
    is_equal: bool
    diff: Optional[str]
    chat_id: Optional[str]

    @classmethod
    def from_record(cls, record: asyncpg.Record) -> 'ConfigurationTest':
        return cls(**dict(record))

    @classmethod
    async def select_by_task_id(
            cls,
            context,
            db_conn,
            task_id: str,
            offset: int,
            limit: int,
            is_equal: Optional[bool] = None,
    ) -> List['ConfigurationTest']:
        query, args = context.sqlt.configuration_test_by_task_id(
            task_id=task_id, offset=offset, limit=limit, is_equal=is_equal,
        )
        rows = await postgres.fetch(db_conn, query, args)
        return list(map(cls.from_record, rows))

    @classmethod
    async def insert(
            cls,
            context,
            db_conn,
            task_id: str,
            request_text: str,
            is_equal: bool,
            diff: Optional[str],
            chat_id: Optional[str],
    ) -> 'ConfigurationTest':
        query, args = context.sqlt.insert_configuration_test(
            task_id=task_id,
            request_text=request_text,
            is_equal=is_equal,
            diff=diff,
            chat_id=chat_id,
        )
        rows = await postgres.fetch(db_conn, query, args)
        assert len(rows) == 1, f'Unexpected num for rows: {len(rows)}'
        return cls.from_record(rows[0])
