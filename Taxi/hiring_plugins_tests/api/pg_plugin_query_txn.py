from hiring_plugins_tests.generated.service.swagger import models  # noqa I202
from hiring_plugins_tests.generated.service.swagger import requests
from hiring_plugins_tests.generated.service.swagger import responses
from hiring_plugins_tests.generated.web import web_context


async def handle(
        request: requests.PgPluginQueryTxn, context: web_context.Context,
) -> responses.PG_PLUGIN_QUERY_TXN_RESPONSES:

    isql = context.postgres_queries['insert-kv.sql']
    ssql = context.postgres_queries['select-kv.sql']

    try:
        async with context.postgresql() as conn:
            async with conn.transaction():
                rows = await conn.fetch(isql, request.key, request.value)
                row = dict(rows[0])
                assert row == {'key': request.key, 'value': request.value}
                raise RuntimeError('test')
    except RuntimeError:
        pass

    async with context.postgresql() as conn:
        rows = await conn.fetch(ssql, request.key)
        assert not rows

    async with context.postgresql() as conn:
        async with conn.transaction():
            rows = await conn.execute(isql, request.key, request.value)

    async with context.postgresql() as conn:
        rows = await conn.fetch(ssql, request.key)

    return responses.PgPluginQueryTxn200(
        data=models.api.PgPluginQueryResponse(
            key=rows[0]['key'], value=rows[0]['value'],
        ),
    )
