# pylint: disable=W0612,C0103
import typing

import pytest


class _Sentinel:
    pass


DEFAULT_PLACE_ID = 123
SENTINEL = _Sentinel()


def value_or_default(value, default):
    return default if value is SENTINEL else value


def make_pytest_param(
        *,
        id: str,  # pylint: disable=redefined-builtin, invalid-name
        marks=(),
        lines: typing.Any = ['a', 'b', 'c', 'd'],
):
    return pytest.param(lines, id=id, marks=marks)


@pytest.mark.pgsql('eats_authorize_personal_manager', files=['add_info.sql'])
@pytest.mark.parametrize(('lines',), (make_pytest_param(id='success'),))
async def test_get_admin_list(web_app_client, load_json, lines):
    response = await web_app_client.post('/admin/v1/line/list')
    response_json = await response.json()
    assert [row['line'] for row in response_json['lines']] == lines
