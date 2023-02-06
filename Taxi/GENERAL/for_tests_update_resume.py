import typing

from taxi.util import dates

from hiring_replica_zarplataru.generated.service.swagger import requests
from hiring_replica_zarplataru.generated.service.swagger import responses
from hiring_replica_zarplataru.generated.web import web_context
from hiring_replica_zarplataru.internal import task_context


async def handle(
        data: requests.ForTestsUpdateResume, context: web_context.Context,
) -> responses.FOR_TESTS_UPDATE_RESUME_RESPONSES:
    if not context.fortest.test_handlers_enabled:
        return responses.ForTestsUpdateResume404()

    ctx = task_context.Web(
        context, 'update_contacts_updated', data.log_extra or {},
    )

    was_updated = await _update_resume(
        ctx, data.body.resume_id, data.body.fields,
    )
    if not was_updated:
        return responses.ForTestsUpdateResume404()

    return responses.ForTestsUpdateResume200()


async def _update_resume(
        ctx: task_context.Web, resume_id: int, fields: typing.List[dict],
) -> bool:
    query, args = ctx.generated.sqlt(
        'tests/update_resume_fields.sqlt',
        {'resume_id': resume_id, 'fields': map(_prepare_field, fields)},
    )
    async with ctx.generated.postgresql(db='hiring_misc') as conn:
        rows = await conn.fetch(query, *args)
    return bool(rows)


def _prepare_field(field_value: dict) -> dict:
    field = field_value['field']
    raw_value = field_value['value']
    if field == 'contacts_updated':
        field_value['value'] = dates.parse_timestring(raw_value)
    else:
        # support another fields if you need it for tests
        raise RuntimeError('unsupported field %s' % field)
    return field_value
