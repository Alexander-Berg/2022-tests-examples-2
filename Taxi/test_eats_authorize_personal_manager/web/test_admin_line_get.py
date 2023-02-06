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
        place_id: typing.Any = DEFAULT_PLACE_ID,
        line_id: typing.Any = 1,
):
    return pytest.param(place_id, line_id, id=id, marks=marks)


@pytest.mark.pgsql('eats_authorize_personal_manager', files=['add_info.sql'])
@pytest.mark.parametrize(
    ('place_id', 'line_id'),
    (
        make_pytest_param(id='success'),
        make_pytest_param(id='success-2', place_id=321, line_id=2),
        make_pytest_param(id='without', place_id=222, line_id=None),
    ),
)
async def test_get_admin_get(web_app_client, load_json, place_id, line_id):
    response = await web_app_client.post(
        '/admin/v1/line/current', json={'place_id': place_id},
    )
    response_json = await response.json()
    assert response_json['place_id'] == place_id
    assert response_json['line_id'] == line_id
