from copy import deepcopy
import pytest
from mouse import Mouse, Has
from ymlcfg.jpath import JPath
from stall.client.clickhouse import (
    FAILS_LIMIT,
    FAILS_TIMEOUT,
    ClickHouseClient,
    ClickHouseClientPool,
    ClickhouseRequestError,
    ClickhouseResponseError,
)


async def test_current_database(tap, clickhouse_client):
    # pylint: disable=unused-argument
    tap.plan(2, 'Проверим, что бд верная')
    class Response(Mouse):
        database = Has(types=str)

    client = ClickHouseClient('grocery')
    response = await client.request_query(
        query='SELECT currentDatabase() as "database"',
        response_format=Response
    )

    tap.eq(len(response), 1, '1 строка в ответе')
    with response[0] as row:
        tap.eq(row.database, 'test_db', 'database')


async def test_request_without_format(tap, clickhouse_client):
    # pylint: disable=unused-argument
    tap.plan(3, 'Запрос без указания формата')

    client = ClickHouseClient('grocery')
    response = await client.request_query(
        query='SELECT currentDatabase() as "database"',
        response_format=None
    )
    response = JPath(response)

    tap.ok(response('data'), 'data есть')
    tap.ok(response('data.0'), '1 строка в data')
    tap.eq(response('data.0.database'), 'test_db', 'database')

@pytest.fixture
def ch_mock_pool(uuid, cfg):
        # pylint: disable=protected-access
    cfg._lazy_load()

    def create_pool(new_urls):
        alias = uuid()
        cfg._db.o['clickhouse'][alias] = deepcopy(
            cfg._db.o['clickhouse']['grocery']
        )
        cfg.set(
            f'clickhouse.{alias}.domains',
            new_urls
        )

        return ClickHouseClientPool(alias)
    return create_pool

@pytest.mark.parametrize(
    'domains,candidate_count',
    [
        (
            ['first'],
            1
        ),
        (
            ['first', 'second'],
            2
        ),
        (
            ['first', 'second', 'third'],
            2
        ),
        (
            ['first', 'second', 'third', 'fourth'],
            3
        ),
    ]
)
async def test_candidates(tap, ch_mock_pool, domains, candidate_count):
    # pylint: disable=redefined-outer-name
    tap.plan(2, 'Тестируем выборку серверов n/2 + 1')
    pool = ch_mock_pool(domains)
    candidates = pool.get_candidates()
    tap.eq(len(candidates), candidate_count,
           f'{len(domains)} сервер, {candidate_count} кандидат')
    tap.ok(
        all(it in pool.clients for it in candidates),
        'Кандидаты из набора клиентов'
    )


@pytest.fixture
def pool_with_log(uuid, cfg, clickhouse_client):
    # pylint: disable=protected-access,unused-argument
    cfg._lazy_load()

    def create_pool(new_urls):
        alias = uuid()
        cfg._db.o['clickhouse'][alias] = deepcopy(
            cfg._db.o['clickhouse']['grocery']
        )
        cfg.set(
            f'clickhouse.{alias}.domains',
            new_urls + cfg(f'clickhouse.{alias}.domains')
        )

        class ClickHouseClientLog(ClickHouseClient):
            async def request_query(self, *args, **kwargs):
                ClickHouseClientPoolMock.request_log.append(self.base_url)
                return await super().request_query(*args, **kwargs)

        class ClickHouseClientPoolMock(ClickHouseClientPool):
            _client = ClickHouseClientLog
            request_log = []

            def get_candidates(self, force=False):
                candidates = self.clients[:]
                return candidates[:len(candidates) // 2 + 1]

        return ClickHouseClientPoolMock(alias)

    return create_pool


async def test_first_good_request(tap, cfg, pool_with_log):
    # pylint: disable=redefined-outer-name
    tap.plan(5, 'Отправка запроса с первой попытки')

    class Response(Mouse):
        key = Has(types=str)

    pool = pool_with_log([])
    tap.eq(len(pool.request_log), 0, 'Лог запросов пуст')

    response = await pool.request_query(
        query='SELECT currentDatabase() as "key"',
        response_format=Response
    )
    tap.eq(len(response), 1, 'Ответ от КХ получен')
    tap.eq(response[0].key, 'test_db', 'Ответ содержит верные данные')

    tap.eq(len(pool.request_log), 1, '1 записи в логе')
    tap.in_ok(cfg('clickhouse.grocery.domains.0'), pool.request_log[0],
              'Лог. Запрос на хороший хост')


async def test_second_good_request(tap, cfg, pool_with_log):
    # pylint: disable=redefined-outer-name
    tap.plan(7, 'Отправка запроса со второй попытки')

    class Response(Mouse):
        key = Has(types=str)

    pool = pool_with_log(['first-try'])
    tap.eq(len(pool.request_log), 0, 'Лог запросов пуст')

    response = await pool.request_query(
        query='SELECT currentDatabase() as "key"',
        response_format=Response
    )
    tap.eq(len(response), 1, 'Ответ от КХ получен')
    tap.eq(response[0].key, 'test_db', 'Ответ содержит верные данные')

    tap.eq(len(pool.request_log), 2, '2 записи в логе')
    tap.in_ok('first-try', pool.request_log[0], 'Лог. Запрос на плохой хост')
    tap.in_ok(cfg('clickhouse.grocery.domains.0'), pool.request_log[1],
              'Лог. Запрос на хороший хост')
    tap.eq(
        sorted(list(pool.fails.values())),
        [0, 1],
        'Один фейл записан'
    )


async def test_bad_request(tap, pool_with_log):
    # pylint: disable=redefined-outer-name
    tap.plan(6, 'Неудачные попытки отправить запрос')

    class Response(Mouse):
        key = Has(types=str)

    pool = pool_with_log(['first-try', 'second-try'])
    tap.eq(len(pool.request_log), 0, 'Лог запросов пуст')

    response = await pool.request_query(
        query='SELECT currentDatabase() as "key"',
        response_format=Response,
        raise_exception=False,
    )
    tap.eq(len(response), 0, 'Пустой ответ')

    tap.eq(len(pool.request_log), 2, '2 записи в логе')
    tap.in_ok('first-try', pool.request_log[0], 'Лог. Запрос на плохой хост')
    tap.in_ok('second-try', pool.request_log[1], 'Лог. Запрос на плохой хост')
    tap.eq(
        sorted(list(pool.fails.values())),
        [0, 1, 1],
        'Два фейла'
    )


async def test_bad_request_with_exc(tap, pool_with_log):
    # pylint: disable=redefined-outer-name
    tap.plan(5, 'Неудачные попытки отправить запрос')

    class Response(Mouse):
        key = Has(types=str)

    pool = pool_with_log(['first-try', 'second-try'])
    tap.eq(len(pool.request_log), 0, 'Лог запросов пуст')

    with tap.raises((ClickhouseRequestError, ClickhouseResponseError)):
        await pool.request_query(
            query='SELECT currentDatabase() as "key"',
            response_format=Response,
        )

    tap.eq(len(pool.request_log), 2, '2 записи в логе')
    tap.in_ok('first-try', pool.request_log[0], 'Лог. Запрос на плохой хост')
    tap.in_ok('second-try', pool.request_log[1], 'Лог. Запрос на плохой хост')


async def test_replace(tap, cfg, uuid):
    with tap.plan(1, 'Замена алиасов таблиц на реальные'):
        table_delivered = uuid()
        table_return_depot = uuid()
        cfg.set('clickhouse.grocery.tables', {
            'grocery_order_delivered': table_delivered,
            'performer_return_depot': table_return_depot
        })

        query = '''
            SELECT * from `grocery_order_delivered`
            UNION ALL
            SELECT * from `grocery_order_delivered`
            UNION ALL
            SELECT * from `performer_return_depot`
        '''
        client = ClickHouseClient('grocery')
        replaced_query = client.replace_table_aliases(query)

        check_query = f'''
            SELECT * from "{table_delivered}"
            UNION ALL
            SELECT * from "{table_delivered}"
            UNION ALL
            SELECT * from "{table_return_depot}"
        '''
        tap.eq(replaced_query, check_query, 'Замена прошла успешно')


async def test_select_candidates(tap, time_mock):
    # pylint: disable=redefined-outer-name
    with tap.plan(7, 'candidates'):
        pool = ClickHouseClientPool('grocery')

        tap.note('Холодный старт ошибок нет')
        candidates = pool.get_candidates()
        tap.eq(len(candidates), 1, '1 кандитат')
        tap.eq(pool.fails[candidates[0]], 0, 'Фейлов нет')

        tap.note('Немного ошибок есть')
        pool.fails[candidates[0]] = FAILS_LIMIT // 2
        candidates = pool.get_candidates()
        tap.eq(len(candidates), 1, '1 кандитат')
        tap.ok(pool.fails[candidates[0]], 'Фейлов есть')

        tap.note('Много ошибок, кандидат уходит')
        pool.fails[candidates[0]] = FAILS_LIMIT + 1
        candidates = pool.get_candidates()
        tap.eq(len(candidates), 0, '0 кандитатов')

        tap.note('Ресет ошибок по времени. Кандидат возвращается')
        time_mock.sleep(seconds=FAILS_TIMEOUT + 1)
        candidates = pool.get_candidates()
        tap.eq(len(candidates), 1, '1 кандитат')
        tap.eq(pool.fails[candidates[0]], 0, 'Фейлов нет')
