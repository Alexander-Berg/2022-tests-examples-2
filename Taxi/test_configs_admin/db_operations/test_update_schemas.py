import pytest

from configs_admin import db_wrappers
from configs_admin.generated.service.swagger.models.api import db_models


@pytest.mark.parametrize(
    'before,after,schemas',
    [
        ('empty_before', 'empty_after', 'empty_schemas'),
        ('empty_before', 'one_schema_after', 'one_schema'),
    ],
)
async def test_db_case(web_context, load_json, before, after, schemas):
    docs, check = await _get_docs_before(load_json, web_context, before)
    assert docs == check

    body_schemas = await _get_schemas(load_json, schemas)
    await db_wrappers.update_schemas(context=web_context, schemas=body_schemas)

    docs, check = await _get_docs_after(load_json, web_context, after)
    assert docs == check


async def _get_docs_before(load_json, context, file_name):
    docs_before = await context.mongo.uconfigs_schemas.find().to_list(None)
    return docs_before, load_json(file_name + '.json')


async def _get_schemas(load_json, file_name):
    body_schemas = load_json(file_name + '.json')
    if not body_schemas:
        return {}

    return {
        item['name']: db_models.SchemaEntity(**item) for item in body_schemas
    }


async def _get_docs_after(load_json, context, file_name):
    docs_after = await context.mongo.uconfigs_schemas.find().to_list(None)
    for doc in docs_after:
        doc.pop('updated', None)
    return docs_after, load_json(file_name + '.json')
