from libstall.util import time2time
from tests.model.clickhouse.base_model import (
    TopicModel
)
from tests.model.clickhouse.grocery.grocery_order_created import (
    GroceryOrderCreated,
)


async def test_create_drop_table(tap, cfg, uuid, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(4, 'Создадим и удалим таблицу'):
        table_name = uuid()
        tables = cfg('clickhouse.grocery.tables')
        tables[table_name] = table_name

        class MockTopic(TopicModel):
            @staticmethod
            def table_alias():
                return table_name

        client = clickhouse_client('grocery')
        table = MockTopic.table_alias()

        response = await client.request_query(
            query=MockTopic.create_query(),
            response_format=None
        )
        tap.eq(response, None, 'Таблица создана')

        response = await client.request_query(
            query=f''' SHOW TABLES FROM test_db LIKE '`{table}`' ''',
            response_format=None
        )
        tap.eq(response['rows'], 1, 'Да, действительно создана')

        response = await client.request_query(
            query=MockTopic.drop_query(),
            response_format=None
        )
        tap.eq(response, None, 'Таблица удалена')

        response = await client.request_query(
            query=f''' SHOW TABLES FROM test_db LIKE '`{table}`' ''',
            response_format=None
        )
        tap.eq(response['rows'], 0, 'Да, действительно удалена')


async def test_insert(tap, now, uuid, clickhouse_client):
    with tap.plan(8, 'Вставим данные в таблицу'):
        client = clickhouse_client('grocery')
        origin = GroceryOrderCreated(
            timestamp=now(),
            depot_id=uuid(),
            order_id=uuid(),
            max_eta=3600,
            delivery_type='dispatch'
        )

        select_query = (f'SELECT * FROM `{origin.table_alias()}` '
                        f' WHERE "depot_id" = \'{origin.depot_id}\'')

        response = await client.request_query(
            query=select_query,
            response_format=GroceryOrderCreated,
        )
        tap.eq(len(response), 0, 'В таблице пока ничего нет')

        response = await client.request_query(
            query=origin.insert_query(),
            response_format=None
        )
        tap.eq(response, None, 'Вставили запись')

        response = await client.request_query(
            query=select_query,
            response_format=GroceryOrderCreated,
        )
        tap.eq(len(response), 1, '1 запись в ответе')
        with response[0] as message:
            tap.eq(message.timestamp, time2time(origin.timestamp), 'timestamp')
            tap.eq(message.depot_id, origin.depot_id, 'depot_id')
            tap.eq(message.order_id, origin.order_id, 'order_id')
            tap.eq(message.max_eta, origin.max_eta, 'max_eta')
            tap.eq(message.delivery_type, origin.delivery_type, 'delivery_type')
