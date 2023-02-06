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
        line: typing.Any = 'q',
        lines: typing.Any = ['a', 'b', 'c', 'd', 'q'],
        response_status: typing.Any = 200,
):
    return pytest.param(line, lines, response_status, id=id, marks=marks)


@pytest.mark.pgsql('eats_authorize_personal_manager', files=['add_info.sql'])
@pytest.mark.parametrize(
    ('line', 'lines', 'response_status'),
    (
        make_pytest_param(id='success'),
        make_pytest_param(id='wrong', line='a', response_status=400),
        make_pytest_param(id='wrong_d', line='d', response_status=400),
    ),
)
async def test_get_admin_bind(
        web_app_client, load_json, line, lines, response_status,
):
    response = await web_app_client.post(
        '/admin/v1/line/bind', json={'line': line},
    )
    assert response.status == response_status
    if response.status == 200:
        response_json = await response.json()
        assert [row['line'] for row in response_json['lines']] == lines
