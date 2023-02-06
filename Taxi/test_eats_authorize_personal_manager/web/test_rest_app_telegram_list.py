# pylint: disable=W0612,C0103
import typing

import pytest


class _Sentinel:
    pass


DEFAULT_PLACE_IDS = [123]
SENTINEL = _Sentinel()


def value_or_default(value, default):
    return default if value is SENTINEL else value


def make_pytest_param(
        *,
        id: str,  # pylint: disable=redefined-builtin, invalid-name
        marks=(),
        place_ids: typing.Any = DEFAULT_PLACE_IDS,
        logins: typing.Any = [{'login': 'a'}, {'login': 'b'}, {'login': 'd'}],
        has_line: typing.Any = True,
        response_status: typing.Any = 200,
        status_restapp: typing.Any = 200,
):
    return pytest.param(
        place_ids,
        logins,
        has_line,
        response_status,
        status_restapp,
        id=id,
        marks=marks,
    )


@pytest.mark.config(
    EATS_AUTHORIZE_PERSONAL_MANAGER_SETTINGS={'logins_limit': 2},
)
@pytest.mark.pgsql('eats_authorize_personal_manager', files=['add_info.sql'])
@pytest.mark.parametrize(
    ('place_ids', 'logins', 'has_line', 'response_status', 'status_restapp'),
    (
        make_pytest_param(id='success'),
        make_pytest_param(
            id='success_none', place_ids=[999], has_line=False, logins=[],
        ),
        make_pytest_param(
            id='permission_den', response_status=403, status_restapp=403,
        ),
    ),
)
async def test_get_admin_acc(
        web_app_client,
        load_json,
        eats_restapp_authorizer_mock,
        place_ids,
        logins,
        has_line,
        response_status,
        status_restapp,
):
    response = await web_app_client.post(
        '/4.0/restapp-front/personal-manager/v1/telegram/list',
        headers={'X-YaEda-PartnerId': '123'},
        json={'place_ids': place_ids},
    )
    assert response.status == response_status
    if response.status == 200:
        response_json = await response.json()
        assert response_json['meta']['logins_limit'] == 2
        assert response_json['payload'][0]['place_id'] == place_ids[0]
        assert response_json['payload'][0]['has_line'] == has_line
        assert response_json['payload'][0]['logins'] == logins
