import datetime
import gzip
import json
import typing

from taxi.util import dates

from hiring_replica_zarplataru.generated.service.swagger import requests
from hiring_replica_zarplataru.generated.service.swagger import responses
from hiring_replica_zarplataru.generated.web import web_context
from hiring_replica_zarplataru.internal import task_context


async def handle(
        request: requests.ForTestsAllResumesAndHistory,
        context: web_context.Context,
) -> responses.FOR_TESTS_ALL_RESUMES_AND_HISTORY_RESPONSES:
    if not context.fortest.test_handlers_enabled:
        return responses.ForTestsAllResumesAndHistory404()

    ctx = task_context.Web(
        context, 'all_resumes_and_history', request.log_extra or {},
    )
    data = {
        'resumes': await _get_resumes(ctx),
        'history': await _get_history(ctx),
    }
    return responses.ForTestsAllResumesAndHistory200(data)


async def _get_resumes(ctx: task_context.Web) -> typing.List[dict]:
    query = ctx.generated.postgres_queries['tests/get_all_resumes.sql']
    async with ctx.generated.postgresql(db='hiring_misc') as conn:
        rows = await conn.fetch(query)

    resumes = []
    for record in rows:
        entry = {}
        for key, value in record.items():
            if key == 'raw_doc':
                entry[key] = json.loads(value)
            elif isinstance(value, datetime.datetime):
                entry[key] = dates.timestring(value)
            else:
                entry[key] = value
        resumes.append(entry)

    return resumes


async def _get_history(ctx: task_context.Web) -> typing.List[dict]:
    query = ctx.generated.postgres_queries['tests/get_all_history.sql']
    async with ctx.generated.postgresql(db='hiring_misc') as conn:
        rows = await conn.fetch(query)

    history = []
    for record in rows:
        entry = {}
        for key, value in record.items():
            if key == 'gzipped_raw_doc':
                entry[key] = json.loads(gzip.decompress(value))
            elif isinstance(value, datetime.datetime):
                entry[key] = dates.timestring(value)
            else:
                entry[key] = value
        history.append(entry)

    return history
