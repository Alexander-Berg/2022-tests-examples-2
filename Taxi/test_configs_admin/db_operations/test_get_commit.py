import pytest

from configs_admin import storage
from test_configs_admin.db_operations import common as c


@pytest.mark.parametrize(
    c.Case.get_args(),
    [
        pytest.param(
            *c.Case(method_name='get_groups_commits', expected={}),
            marks=pytest.mark.filldb(uconfigs_meta='empty'),
            id='first launch',
        ),
        pytest.param(
            *c.Case(
                method_name='get_groups_commits',
                expected={
                    'devicenotify': '9055f4b5a86ed0ab805804d8b5ce277903492c54',
                    'CONFIG_SCHEMAS_META_ID': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                },
            ),
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
    assert result == expected
