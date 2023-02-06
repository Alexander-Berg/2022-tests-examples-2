import datetime

import pytest

from configs_admin import storage
from configs_admin.generated.service.swagger.models.api import db_models
from test_configs_admin.db_operations import common as c


@pytest.mark.parametrize(
    c.Case.get_args(),
    [
        pytest.param(
            *c.Case(
                method_name='fetch_by_name',
                args=['SCHEMA_WITH_REF'],
                expected=db_models.SchemaEntity(
                    name='SCHEMA_WITH_REF',
                    version=2,
                    schema={
                        'value': {'$ref': '/definitions/Value'},
                        'definitions': {'Value': {'type': 'number'}},
                    },
                    group='folder_name',
                    default={'value': 123},
                    last_updated_time=datetime.datetime(2019, 3, 6, 11, 0),
                ).serialize(),
                post_processing=lambda x: x.serialize(),
            ),
        ),
        pytest.param(
            *c.Case(
                method_name='fetch_versions',
                kwargs={'names': ['SIMPLE_SCHEMA', 'SCHEMA_WITH_REF']},
                expected={'SCHEMA_WITH_REF': 2, 'SIMPLE_SCHEMA': 1},
            ),
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
    db_schema = storage.DbSchema(context=web_context)
    method = getattr(db_schema, method_name)

    result = await method(*args, **kwargs)
    assert post_processing(result) == expected
