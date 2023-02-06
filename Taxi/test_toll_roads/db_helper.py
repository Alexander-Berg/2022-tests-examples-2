import datetime
import typing

from test_toll_roads import queries
from toll_roads.generated.stq3 import stq_context
from toll_roads.generated.web import web_context


class DbHelper:
    def __init__(
            self,
            context: typing.Union[web_context.Context, stq_context.Context],
    ):
        self.context = context

    async def save_offer(self, offer_id: str):
        async with self.context.pg.master_pool.acquire() as conn:
            await conn.execute(queries.OFFER_SAVE_SQL, offer_id)

    async def save_order(
            self,
            order_id: str,
            created_at: datetime.datetime,
            can_switch_road: bool,
            offer_id: str,
            auto_payment: typing.Optional[bool] = None,
            source: typing.Optional[str] = None,
            destination: typing.Optional[str] = None,
    ):
        async with self.context.pg.master_pool.acquire() as conn:
            await conn.execute(
                queries.ORDER_SAVE_SQL,
                order_id,
                created_at,
                can_switch_road,
                offer_id,
                auto_payment if auto_payment else False,
                source,
                destination,
            )

    async def save_log(
            self,
            order_id: str,
            created_at: datetime.datetime,
            user_chose_toll_roads: bool,
    ):
        async with self.context.pg.master_pool.acquire() as conn:
            await conn.execute(
                queries.LOG_SAVE_SQL,
                order_id,
                created_at,
                user_chose_toll_roads,
            )

    async def fetch_offer(self, offer_id: str):
        async with self.context.pg.master_pool.acquire() as conn:
            return await conn.fetchrow(queries.OFFER_FETCH_SQL, offer_id)

    async def fetch_order(self, order_id: str):
        async with self.context.pg.master_pool.acquire() as conn:
            return await conn.fetchrow(queries.ORDER_FETCH_SQL, order_id)

    async def fetch_last_log(self, order_id: str):
        async with self.context.pg.master_pool.acquire() as conn:
            return await conn.fetchrow(queries.LOG_FETCH_LAST_SQL, order_id)
