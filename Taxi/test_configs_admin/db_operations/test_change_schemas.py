import pytest

from configs_admin import storage
from test_configs_admin.db_operations import common as c


@pytest.mark.parametrize(
    c.Case.get_args(),
    [
        pytest.param(
            *c.Case(
                method_name='remove_by_names',
                kwargs={'names': ['SIMPLE_SCHEMA']},
                expected=['SCHEMA_WITH_REF'],
            ),
            id='remove_by_names: success remove target',
        ),
        pytest.param(
            *c.Case(
                method_name='remove_by_names',
                kwargs={'names': ['UNKNOWN']},
                expected=['SIMPLE_SCHEMA', 'SCHEMA_WITH_REF'],
                ignore_fields=['true'],
            ),
            id='remove_by_names: no change if target not found',
        ),
        pytest.param(
            *c.Case(
                method_name='remove_by_names',
                kwargs={'names': ['SIMPLE_SCHEMA', 'SCHEMA_WITH_REF']},
                expected=[],
            ),
            id='remove_by_names: all',
        ),
    ],
)
async def test_case(
        web_context,
        method_name,
        args,
        kwargs,
        ignore_fields,
        expected,
        post_processing,
):
    cursor = web_context.mongo.uconfigs_schemas.find(
        projection=[storage.SCHEMA_FIELDS.NAME],
    ).to_list(None)
    docs_before = await cursor
    all_names = [item[storage.SCHEMA_FIELDS.NAME] for item in docs_before]

    db_schema = storage.DbSchema(context=web_context)
    method = getattr(db_schema, method_name)

    await method(*args, **kwargs)
    cursor = web_context.mongo.uconfigs_schemas.find(
        projection=[storage.SCHEMA_FIELDS.NAME],
    ).to_list(None)
    docs_after = await cursor
    if 'true' not in ignore_fields:
        assert docs_before != docs_after

    response = await db_schema.fetch_versions(names=all_names)
    assert sorted(response.keys()) == sorted(expected)
