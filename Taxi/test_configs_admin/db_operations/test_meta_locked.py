import datetime

import pytest

from configs_admin import storage
from test_configs_admin.db_operations import common as c


@pytest.mark.parametrize(
    c.Case.get_args(),
    [
        pytest.param(
            *c.Case(
                method_name='lock',
                expected={
                    'current_hash': 'b805804d8b5ce277903492c549055f4b5a86ed0a',
                    'no_change_time': '2119-03-06T16:00:00+03:00',
                    'updated': '2019-03-06T14:00:00+03:00',
                    'group': 'CONFIG_SCHEMAS_META_ID',
                },
                kwargs={
                    'now': datetime.datetime.fromisoformat(
                        '2119-03-06T15:00:00+03:00',
                    ),
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'lock_to': datetime.datetime.fromisoformat(
                        '2119-03-06T16:00:00+03:00',
                    ),
                },
            ),
            marks=pytest.mark.filldb(uconfigs_meta='locked'),
            id='check lock',
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
    doc_before = await web_context.mongo.uconfigs_meta.find_one(
        {storage.META_FIELDS.DOC: storage.CONFIG_SCHEMAS_META_ID},
    )
    db_schema = storage.DbMeta(context=web_context)
    method = getattr(db_schema, method_name)

    await method(*args, **kwargs)
    doc_after = await web_context.mongo.uconfigs_meta.find_one(
        {storage.META_FIELDS.DOC: storage.CONFIG_SCHEMAS_META_ID},
    )
    assert doc_before != doc_after

    response = await db_schema.get_meta()
    result = {
        key: value
        for key, value in response.serialize().items()
        if key not in ignore_fields
    }
    assert result == {
        key: value
        for key, value in expected.items()
        if key not in ignore_fields
    }
