import dataclasses
from typing import Optional  # noqa: IS001

import asyncpg

from supportai_lib.utils import postgres


@dataclasses.dataclass
class TestingAggregation:
    id: int  # pylint: disable=invalid-name
    task_id: str
    ok_chat_count: int
    chat_count: int
    equal_count: int
    topic_ok_count_v1: int
    topic_ok_count_v2: int
    reply_count_v1: int
    reply_count_v2: int
    close_count_v1: int
    close_count_v2: int
    reply_or_close_count_v1: int
    reply_or_close_count_v2: int
    topic_details: str

    @classmethod
    def from_record(cls, record: asyncpg.Record) -> 'TestingAggregation':
        return cls(**dict(record))

    @classmethod
    async def select_by_task_id(
            cls, context, db_conn, task_id: str,
    ) -> Optional['TestingAggregation']:
        query, args = context.sqlt.testing_aggregation_by_task_id(
            task_id=task_id,
        )
        rows = await postgres.fetch(db_conn, query, args)
        return cls.from_record(rows[0]) if len(rows) == 1 else None

    @classmethod
    async def insert(
            cls,
            context,
            db_conn,
            task_id: str,
            ok_chat_count: int = 0,
            chat_count: int = 0,
            equal_count: int = 0,
            topic_ok_count_v1: int = 0,
            topic_ok_count_v2: int = 0,
            reply_count_v1: int = 0,
            reply_count_v2: int = 0,
            close_count_v1: int = 0,
            close_count_v2: int = 0,
            reply_or_close_count_v1: int = 0,
            reply_or_close_count_v2: int = 0,
            topic_details: str = '{}',
    ) -> 'TestingAggregation':
        query, args = context.sqlt.insert_testing_aggregation(
            task_id=task_id,
            ok_chat_count=ok_chat_count,
            chat_count=chat_count,
            equal_count=equal_count,
            topic_ok_count_v1=topic_ok_count_v1,
            topic_ok_count_v2=topic_ok_count_v2,
            reply_count_v1=reply_count_v1,
            reply_count_v2=reply_count_v2,
            close_count_v1=close_count_v1,
            close_count_v2=close_count_v2,
            reply_or_close_count_v1=reply_or_close_count_v1,
            reply_or_close_count_v2=reply_or_close_count_v2,
            topic_details=topic_details,
        )
        rows = await postgres.fetch(db_conn, query, args)
        assert len(rows) == 1, f'Unexpected num for rows: {len(rows)}'
        return cls.from_record(rows[0])

    @classmethod
    async def update(
            cls, context, db_conn, aggregation: 'TestingAggregation',
    ) -> None:
        query, args = context.sqlt.update_testing_aggregation_by_task_id(
            task_id=aggregation.task_id,
            ok_chat_count=aggregation.ok_chat_count,
            chat_count=aggregation.chat_count,
            equal_count=aggregation.equal_count,
            topic_ok_count_v1=aggregation.topic_ok_count_v1,
            topic_ok_count_v2=aggregation.topic_ok_count_v2,
            reply_count_v1=aggregation.reply_count_v1,
            reply_count_v2=aggregation.reply_count_v2,
            close_count_v1=aggregation.close_count_v1,
            close_count_v2=aggregation.close_count_v2,
            reply_or_close_count_v1=aggregation.reply_or_close_count_v1,
            reply_or_close_count_v2=aggregation.reply_or_close_count_v2,
            topic_details=aggregation.topic_details,
        )
        await postgres.execute(db_conn, query, args)
