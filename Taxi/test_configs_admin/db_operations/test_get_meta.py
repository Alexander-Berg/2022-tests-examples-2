import datetime

import pytest

from configs_admin import storage
from configs_admin.generated.service.swagger.models.api import db_models
from test_configs_admin.db_operations import common as c


@pytest.mark.parametrize(
    c.Case.get_args(),
    [
        pytest.param(
            *c.Case(method_name='get_meta', expected=None),
            marks=pytest.mark.filldb(uconfigs_meta='empty'),
            id='first launch',
        ),
        pytest.param(
            *c.Case(
                method_name='get_meta',
                expected=db_models.MetaEntity(
                    group='CONFIG_SCHEMAS_META_ID',
                    current_hash='b805804d8b5ce277903492c549055f4b5a86ed0a',
                    updated=datetime.datetime.fromisoformat(
                        '2019-03-06T14:00:00+03:00',
                    ),
                ).serialize(),
                post_processing=lambda x: x.serialize(),
            ),
            id='already updated',
        ),
        pytest.param(
            *c.Case(
                method_name='get_meta',
                expected=db_models.MetaEntity(
                    group='CONFIG_SCHEMAS_META_ID',
                    current_hash='b805804d8b5ce277903492c549055f4b5a86ed0a',
                    updated=datetime.datetime.fromisoformat(
                        '2019-03-06T14:00:00+03:00',
                    ),
                    sent=datetime.datetime.fromisoformat(
                        '2019-03-06T14:00:00+03:00',
                    ),
                    prev_hash='2c549055f4b5a86ed0ab805804d8b5ce27790349',
                ).serialize(),
                post_processing=lambda x: x.serialize(),
            ),
            marks=pytest.mark.filldb(uconfigs_meta='full'),
            id='already updated',
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
    db_schema = storage.DbMeta(context=web_context)
    method = getattr(db_schema, method_name)

    result = await method(*args, **kwargs)
    assert post_processing(result) == expected
