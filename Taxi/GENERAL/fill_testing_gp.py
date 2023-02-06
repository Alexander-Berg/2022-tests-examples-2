"""Скрипт для наполнения БД greenplum в тестинге данными необходимыми
для проверки сервиса eats-courier-scoring.

Затрагиваются следующие таблицы:
- titovaod_eda_ods_bigfood.courier - таблица с курьерами
- titovaod_taxi_ods_dbdrivers.executor_profile - таблица с профайлами курьеров
- titovaod_eda_cdm_marketplace.dm_order - таблица с заказами

Для того, чтобы не перетереть имеющиеся данные, у всех добавляемых
объектов заведомо больший id чем в проде:
- id курьеров начинается с 31100000
- id заказов начинается с 987600000

!!! Перед добавлением новых курьеров/заказов все записи с id превышающим
стартовый удаляются из БД !!!

Пока доступно только 1 нарушение - damaged_status (когда статус о повреждении
заказа выставлен непосредственно в таблице dm_order).
"""

import argparse
import asyncio
import dataclasses
import datetime
import logging
import os
import ssl
import typing

import asyncpg
import dbtpl

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

START_COURIER_ID = 31100000
START_ORDER_ID = 987600000
ORDER_NR_FIRST = 990000
ORDER_NR_LAST = 0

DATE = (datetime.date.today() - datetime.timedelta(days=1)).strftime(
    '%Y-%m-%d',
)

# считаем, что конфиг настроен следующим образом:
# [ 0- 4] заказов - пропускаем
# [ 5-10] заказов - малое кол-во (малыши)
# [11-25] заказов - обычные курьеры

# Каждый элемент этого списка генерирует `couriers` курьеров, у которых
# `good` хороших заказов и `damaged_status` дефектных заказов.
# Т.е. для элемента
# {'couriers': 5, 'orders': {'good': 5, 'damaged_status': 5}}
# будет создано 5 курьеров с 10 заказами у каждого (сумарно 50 заказов).
RULES = [
    # недостаточное кол-во заказов (< 5)
    {'couriers': 5, 'orders': {'good': 3, 'damaged_status': 0}},
    # малое кол-во заказов
    {'couriers': 5, 'orders': {'good': 5, 'damaged_status': 5}},
    {'couriers': 5, 'orders': {'good': 5}},
    {'couriers': 5, 'orders': {'good': 10}},
    {'couriers': 5, 'orders': {'good': 1, 'damaged_status': 5}},
    {'couriers': 5, 'orders': {'good': 3, 'damaged_status': 7}},
    # обычное кол-во заказов
    {'couriers': 5, 'orders': {'good': 10, 'damaged_status': 5}},
    {'couriers': 5, 'orders': {'good': 15}},
    {'couriers': 5, 'orders': {'good': 10, 'damaged_status': 10}},
    {'couriers': 5, 'orders': {'good': 0, 'damaged_status': 5}},
    {'couriers': 5, 'orders': {'good': 20, 'damaged_status': 5}},
    # большое кол-во заказов
    {'couriers': 3, 'orders': {'good': 30, 'damaged_status': 0}},
    {'couriers': 2, 'orders': {'good': 20, 'damaged_status': 10}},
]

# настройки полей для различных видов наказаний
DEFECT_FIELDS = {
    'good': {
        'order_status': 4,
        'cancel_reason_name': None,
        'cancel_reason_group_name': None,
    },
    'damaged_status': {
        'order_status': 5,
        'cancel_reason_name': 'Заказ поврежден, перепутан или отсутствует',
        'cancel_reason_group_name': 'courier',
    },
}


@dataclasses.dataclass(frozen=True)
class Table:
    schema: str
    name: str

    _sqlt_directory = ''
    _sqlt_agent = None

    @classmethod
    def sqlt_agent(cls, fname, **kwargs):
        if not cls._sqlt_agent:
            if not cls._sqlt_directory:
                raise RuntimeError(
                    f'sqlt directory is not defined for class {cls.__name__}',
                )
            cls._sqlt_agent = dbtpl.agent(
                directory=os.path.join(
                    os.path.dirname(__file__), 'sqlt', cls._sqlt_directory,
                ),
            )
        # pylint: disable=not-callable
        return cls._sqlt_agent(fname, args=kwargs)

    @property
    def fullname(self):
        return f'{self.schema}.{self.name}'


@dataclasses.dataclass(frozen=True)
class Courier(Table):
    versioned: bool = False
    has_revision: bool = False

    _sqlt_directory = 'courier'

    async def add_couriers(
            self,
            *,
            connection: asyncpg.Connection,
            couriers_ids: typing.List[int],
    ):
        query, args = self.sqlt_agent(
            'add_couriers.sqlt', table=self, couriers_ids=couriers_ids,
        )
        await connection.execute(query, *args)

    async def delete_couriers(
            self, *, connection: asyncpg.Connection, start_id: int,
    ):
        query, args = self.sqlt_agent(
            'delete_couriers.sqlt', table=self, start_id=start_id,
        )
        await connection.execute(query, *args)


@dataclasses.dataclass(frozen=True)
class Profile(Table):
    versioned: bool = False
    has_revision: bool = False

    _sqlt_directory = 'profile'

    async def delete_profiles(
            self, *, connection: asyncpg.Connection, start_id: int,
    ):
        query, args = self.sqlt_agent(
            'delete_profiles.sqlt', table=self, start_id=start_id,
        )
        await connection.execute(query, *args)

    async def add_profiles(
            self, *, connection: asyncpg.Connection, couriers_ids,
    ):
        query, args = self.sqlt_agent(
            'add_profiles.sqlt', table=self, couriers_ids=couriers_ids,
        )
        await connection.execute(query, *args)


@dataclasses.dataclass(frozen=True)
class Order(Table):
    versioned: bool = False
    has_revision: bool = False

    _sqlt_directory = 'order'

    async def delete_orders(
            self, *, connection: asyncpg.Connection, start_id: int,
    ):
        query, args = self.sqlt_agent(
            'delete_orders.sqlt', table=self, start_id=start_id,
        )
        await connection.execute(query, *args)

    async def add_orders(self, *, connection: asyncpg.Connection, orders):
        query, args = self.sqlt_agent(
            'add_orders.sqlt', table=self, orders=orders, date=DATE,
        )
        await connection.execute(query, *args)


@dataclasses.dataclass(frozen=True)
class ComplaintTable(Table):
    versioned: bool = False
    has_revision: bool = False

    _sqlt_directory = 'complaint'

    async def delete_complaints(
            self, *, connection: asyncpg.Connection, start_id: int,
    ):
        query, args = self.sqlt_agent(
            'delete_complaints.sqlt', table=self, start_id=start_id,
        )
        await connection.execute(query, *args)

    async def add_complaints(
            self, *, connection: asyncpg.Connection, orders_ids,
    ):
        query, args = self.sqlt_agent(
            'add_complaints.sqlt', table=self, orders_ids=orders_ids,
        )
        await connection.execute(query, *args)


def get_couriers_and_orders(
        rules,
        *,
        start_courier_id=START_COURIER_ID,
        start_order_id=START_ORDER_ID,
        order_nr_first=ORDER_NR_FIRST,
        order_nr_last=ORDER_NR_LAST,
):
    new_couriers = []
    new_orders = []
    for rule in rules:
        couriers_count = rule['couriers']
        for courier_id in range(
                start_courier_id, start_courier_id + couriers_count,
        ):
            new_couriers.append(courier_id)
            for order_type, orders_count in rule['orders'].items():
                for order_id in range(
                        start_order_id, start_order_id + orders_count,
                ):
                    new_orders.append(
                        {
                            'order_id': order_id,
                            'courier_id': courier_id,
                            'order_nr': '%06d-%06d' % (
                                order_nr_first,
                                order_nr_last,
                            ),
                            **DEFECT_FIELDS[order_type],
                        },
                    )
                    order_nr_last += 1
                    start_order_id += 1
            start_courier_id += 1
    return new_couriers, new_orders


async def update_tables(connection, new_couriers, new_orders):
    courier_table = Courier(schema='titovaod_eda_ods_bigfood', name='courier')
    profile_table = Profile(
        schema='titovaod_taxi_ods_dbdrivers', name='executor_profile',
    )
    order_table = Order(schema='titovaod_eda_cdm_marketplace', name='dm_order')
    logger.info('delete couriers')
    await courier_table.delete_couriers(
        connection=connection, start_id=START_COURIER_ID,
    )
    logger.info('delete profiles')
    await profile_table.delete_profiles(
        connection=connection, start_id=START_COURIER_ID,
    )
    logger.info('delete orders')
    await order_table.delete_orders(
        connection=connection, start_id=START_COURIER_ID,
    )

    # insert
    logger.info('insert couriers')
    await courier_table.add_couriers(
        connection=connection, couriers_ids=new_couriers,
    )
    logger.info('insert profiles')
    await profile_table.add_profiles(
        connection=connection, couriers_ids=new_couriers,
    )
    logger.info('insert orders')
    await order_table.add_orders(connection=connection, orders=new_orders)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Not modify db, just prepare data',
    )
    parser.add_argument('--log_queries', action='store_true')
    parser.add_argument('--host', default='gpdb-pgbouncer.taxi.tst.yandex.net')
    parser.add_argument('--database', default='butthead')
    parser.add_argument('--port', default=5432, type=int)
    parser.add_argument('--user', required=True)
    parser.add_argument('--password', required=True)
    return parser.parse_args()


async def main():
    args = parse_args()

    new_couriers, new_orders = get_couriers_and_orders(
        RULES,
        start_courier_id=START_COURIER_ID,
        start_order_id=START_ORDER_ID,
        order_nr_first=ORDER_NR_FIRST,
        order_nr_last=ORDER_NR_LAST,
    )

    logger.info('new_couriers: %d', len(new_couriers))
    logger.info('new_orders: %d', len(new_orders))
    if args.debug:
        logger.info(new_couriers)
        for row in new_orders:
            logger.info(row)
        return

    db_args = {
        'host': args.host,
        'database': args.database,
        'password': args.password,
        'port': args.port,
        'user': args.user,
        'ssl': ssl._create_unverified_context(),
    }

    conn = await asyncpg.connect(**db_args)
    await update_tables(
        connection=conn, new_couriers=new_couriers, new_orders=new_orders,
    )
    await conn.close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
