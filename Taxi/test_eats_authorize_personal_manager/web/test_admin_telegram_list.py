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
        logins: typing.Any = ['a', 'b', 'd'],
):
    return pytest.param(place_id, logins, id=id, marks=marks)


@pytest.mark.config(
    EATS_AUTHORIZE_PERSONAL_MANAGER_SETTINGS={'logins_limit': 2},
)
@pytest.mark.pgsql('eats_authorize_personal_manager', files=['add_info.sql'])
@pytest.mark.parametrize(
    ('place_id', 'logins'),
    (
        make_pytest_param(id='success'),
        make_pytest_param(id='success_one', place_id=321, logins=['c']),
        make_pytest_param(id='without_logins', place_id=222, logins=[]),
    ),
)
async def test_get_admin_acc(web_app_client, load_json, place_id, logins):
    response = await web_app_client.post(
        '/admin/v1/telegram/list', json={'place_id': place_id},
    )
    response_json = await response.json()
    assert response_json['payload']['place_id'] == place_id
    assert response_json['payload']['logins'] == logins
    assert response_json['meta']['logins_limit'] == 2
