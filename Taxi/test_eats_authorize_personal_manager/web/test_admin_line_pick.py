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
        response_status: typing.Any = 204,
):
    return pytest.param(place_id, line_id, response_status, id=id, marks=marks)


@pytest.mark.pgsql('eats_authorize_personal_manager', files=['add_info.sql'])
@pytest.mark.parametrize(
    ('place_id', 'line_id', 'response_status'),
    (
        make_pytest_param(id='success'),
        make_pytest_param(id='success2', place_id=321, line_id=1),
        make_pytest_param(id='success0', place_id=999, line_id=2),
        make_pytest_param(id='wrong', line_id=123, response_status=400),
    ),
)
async def test_get_admin_pick(
        web_app_client, pgsql, load_json, place_id, line_id, response_status,
):
    response = await web_app_client.post(
        '/admin/v1/line/pick', json={'place_id': place_id, 'line_id': line_id},
    )
    assert response.status == response_status
    if response.status == 204:
        assert _get_line_id(pgsql, place_id) == line_id


def _get_line_id(pgsql, place_id):
    with pgsql['eats_authorize_personal_manager'].cursor() as cursor:
        cursor.execute(
            f'select line_id from line_bind_place '
            f'where place_id={place_id}',
        )
        result = cursor.fetchone()
    return result[0]
