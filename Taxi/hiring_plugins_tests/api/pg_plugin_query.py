from taxi import pg

from hiring_plugins_tests.generated.service.swagger import models  # noqa I202
from hiring_plugins_tests.generated.service.swagger import requests
from hiring_plugins_tests.generated.service.swagger import responses
from hiring_plugins_tests.generated.web import web_context


async def handle(
        request: requests.PgPluginQuery, context: web_context.Context,
) -> responses.PG_PLUGIN_QUERY_RESPONSES:

    ssql = context.postgres_queries['select-kv.sql']
    isql = context.postgres_queries['insert-kv.sql']

    async with context.postgresql(shard=0, mode=pg.Slave) as conn:
        await conn.execute(isql, request.key, request.value)
        rows = await conn.fetch(ssql, request.key)

    return responses.PgPluginQuery200(
        data=models.api.PgPluginQueryResponse(
            key=rows[0]['key'], value=rows[0]['value'],
        ),
    )
