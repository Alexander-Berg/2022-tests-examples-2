# pylint: disable=wildcard-import,unused-wildcard-import,unused-import
# pylint: disable=redefined-outer-name

import typing
import uuid

from aiohttp import web
import asyncpg
import pytest

import hiring_st.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from hiring_st.generated.cron import run_cron  # noqa: I100
from hiring_st.internal import cursor as internal_cursor
from taxi.pytest_plugins import service  # noqa: F401 I201 I100

pytest_plugins = ['hiring_st.generated.service.pytest_plugins']


@pytest.fixture(scope='function', autouse=True)
async def pg_restart_sequences(web_context):
    """Сброс счетчиков БД перед тестом. Удобно тестировать идентификаторы."""
    async with web_context.postgresql() as conn:
        await conn.execute(
            """
                SELECT
                    SETVAL("c"."oid", 1, FALSE)
                FROM
                    "pg_class" "c"
                JOIN
                    "pg_namespace" "n" ON "n"."oid" = "c"."relnamespace"
                WHERE
                    "c"."relkind" = 'S'
                    AND "n"."nspname" IN (
                        'hiring_st_misc',
                        'hiring_st_hot',
                        'hiring_st_cold'
                    )
                ;
            """,
        )


@pytest.fixture
async def test_client_ping(web_context, mockserver):
    """Проверка работы клиента"""

    # TODO: когда будет полноценное поднятие окружения для теста, то
    #       выпилить все mock ручки чтобы использовало реальные.
    @mockserver.json_handler('/hiring-st/ping')
    async def handler(request):  # pylint: disable=unused-variable
        return web.Response()

    async def _wrapper():
        response = await web_context.clients.hiring_st.ping()
        assert response.status == 200
        return response

    return _wrapper


@pytest.fixture
def create_workflow(web_app_client):
    """Создание рабочего процесса"""

    async def _wrapper(data, request_id=None) -> str:
        data['request_id'] = request_id or uuid.uuid4().hex

        response = await web_app_client.post('/v1/workflow', json=data)
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def get_workflow(web_app_client):
    """Получение рабочего процесса"""

    async def _wrapper(workflow_id) -> str:
        data = {'workflow_id': workflow_id}
        response = await web_app_client.get('/v1/workflow', params=data)
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def request_queue(web_app_client):
    """Запрос на создание очереди"""

    async def _wrapper(
            data,
            workflow_id: typing.Optional[str] = None,
            description: typing.Optional[str] = None,
    ) -> str:
        if workflow_id is not None:
            data['workflow_id'] = workflow_id
        if description is not None:
            data['description'] = description

        response = await web_app_client.post('/v1/queue', json=data)
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def get_operation(web_app_client):
    """Получить операцию по ее идентификатору"""

    async def _wrapper(data) -> str:
        response = await web_app_client.get(
            '/v1/queue/operations', params=data,
        )
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def get_queue(web_app_client):
    """Получение очереди"""

    async def _wrapper(data) -> str:
        response = await web_app_client.get('/v1/queue', params=data)
        assert response.status == 200, await response.text()
        content = await response.json()
        return content

    return _wrapper


@pytest.fixture
def create_queue(web_app_client):
    """ Создание очереди. Возвращает уже созданную очередь"""

    async def _wrapper(
            data,
            workflow_id: typing.Optional[str] = None,
            description: typing.Optional[str] = None,
    ) -> str:
        if workflow_id is not None:
            data['workflow_id'] = workflow_id
        if description is not None:
            data['description'] = description

        response = await web_app_client.post('/v1/queue', json=data)
        assert response.status == 200

        await run_cron.main(
            ['hiring_st.crontasks.queue_save', '-t', '0', '-d'],
        )

        data2 = {'queue_id': data['queue_id']}
        response = await web_app_client.get('/v1/queue', params=data2)
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def save_queues(web_context):
    """Запуск обработчки операций сохранения очереди"""

    async def _wrapper() -> bool:
        await run_cron.main(
            ['hiring_st.crontasks.queue_save', '-t', '0', '-d'],
        )
        return True

    return _wrapper


@pytest.fixture
def fake_operations_processing(web_context):
    """
    Отмечает операции как взятые в обработку.
    Требуется для теста таймаута.
    """

    async def _wrapper() -> typing.List[asyncpg.Record]:
        async with web_context.postgresql() as conn:
            return await conn.fetch(
                """
                UPDATE
                    "hiring_st_misc"."operations"
                SET
                    "status" = 'processing',
                    "updated_ts" = NOW()::TIMESTAMPTZ(0)
                WHERE
                    "status" = 'pending'
                RETURNING
                    *
                ;
                """,
            )

    return _wrapper


@pytest.fixture
def timeout_operations():
    """Запуск сброса просроченных операций манипуляции с очередью"""

    async def _wrapper() -> bool:
        await run_cron.main(
            ['hiring_st.crontasks.operation_timeout', '-t', '0', '-d'],
        )
        return True

    return _wrapper


@pytest.fixture
def create_draft(web_app_client):
    """Запрос на создание тикета"""

    async def _wrapper(data) -> str:
        response = await web_app_client.post(
            '/v1/tickets/create-draft', json=data,
        )
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def commit_draft(web_app_client):
    """Запрос на коммит тикета"""

    async def _wrapper(ticket_id) -> str:
        response = await web_app_client.post(
            '/v1/tickets/commit', json={'ticket_id': ticket_id},
        )
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def create_ticket(web_app_client):
    """Создание тикета"""

    async def _wrapper(data) -> str:
        response = await web_app_client.post(
            '/v1/tickets/create-draft', json=data,
        )
        assert response.status == 200, await response.text()
        draft = await response.json()

        response = await web_app_client.post(
            '/v1/tickets/commit', json={'ticket_id': draft['ticket_id']},
        )
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def get_ticket(web_app_client):
    """Получение тикета из горячего хранилища"""

    async def _wrapper(data) -> str:
        response = await web_app_client.post(
            '/v1/tickets/get-ticket', json=data,
        )
        assert response.status in (200, 304), await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def get_ticket_cold(web_app_client):
    """Получение тикета из холодного хранилища"""

    async def _wrapper(data=None, ticket_id=None) -> str:
        if data is None:
            data = {}
        if ticket_id is not None:
            data['ticket_id'] = ticket_id
        response = await web_app_client.post(
            '/v1/tickets/get-ticket-slow', json=data,
        )
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def find_ticket(web_app_client):
    """Поиск тикета"""

    async def _wrapper(data) -> str:
        response = await web_app_client.post('/v1/tickets/find', json=data)
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def update_ticket(web_app_client):
    """Обновление тикета"""

    async def _wrapper(data, ticket_id: str = None) -> str:
        if ticket_id is not None:
            data['ticket_id'] = ticket_id

        response = await web_app_client.post(
            '/v1/tickets/update-ticket', json=data,
        )
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def get_oplog(web_app_client):
    """Поиск тикета"""

    async def _wrapper(data) -> str:
        response = await web_app_client.post('/v1/oplog', json=data)
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def get_oplog_slow(web_app_client):
    """Холодная история тикетов"""

    async def _wrapper(data) -> str:
        response = await web_app_client.post('/v1/oplog-slow', json=data)
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def move_to_slow():
    """
        Отправляет старые тикеты в холодное хранилище.
        Возвращает уже созданную очередь
    """

    async def _wrapper() -> bool:
        await run_cron.main(
            ['hiring_st.crontasks.move_to_cold', '-t', '0', '-d'],
        )
        return True

    return _wrapper


@pytest.fixture
def oplog_record_hide(web_context):
    """
        Скрывает запись оплога во временную таблицу
    """

    async def _wrapper(revision) -> bool:
        async with web_context.postgresql() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    CREATE TEMPORARY TABLE IF NOT EXISTS
                        "pg_temp"."tmp_test_oplog_freeze" (
                            LIKE "hiring_st_hot"."history"
                                INCLUDING ALL
                        )
                    ;
                    """,
                )
                await conn.execute(
                    """
                    WITH "row" AS (
                        DELETE FROM
                            "hiring_st_hot"."history"
                        WHERE
                            "revision" = $1::INTEGER
                        RETURNING
                            *
                    )
                    INSERT INTO
                        "pg_temp"."tmp_test_oplog_freeze"
                    SELECT
                        *
                    FROM
                        "row"
                    ;
                    """,
                    revision,
                )
        return True

    return _wrapper


@pytest.fixture
def oplog_record_show(web_context):
    """
        Показывает запись оплога из временной таблицы
    """

    async def _wrapper(revision) -> bool:

        async with web_context.postgresql() as conn:
            await conn.execute(
                """
                    WITH "row" AS (
                        DELETE FROM
                            "pg_temp"."tmp_test_oplog_freeze"
                        WHERE
                            "revision" = $1::INTEGER
                        RETURNING
                            *
                    )
                    INSERT INTO
                        "hiring_st_hot"."history"
                    SELECT
                        *
                    FROM
                        "row"
                    ;
                """,
                revision,
            )
        return True

    return _wrapper


@pytest.fixture
def decode_cursor():
    """
        Возвращает объект курсора из ответа сервера
    """

    def _wrapper(data) -> internal_cursor.Cursor:
        return internal_cursor.Cursor.deserialize(data)

    return _wrapper
