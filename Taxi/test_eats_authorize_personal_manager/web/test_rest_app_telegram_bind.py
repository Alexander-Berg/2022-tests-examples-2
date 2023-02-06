# pylint: disable=W0612,C0103
import typing

import pytest


class _Sentinel:
    pass


DEFAULT_PLACES = [{'place_id': 123, 'logins': ['a', 'b', 'w']}]
SENTINEL = _Sentinel()


def value_or_default(value, default):
    return default if value is SENTINEL else value


def make_pytest_param(
        *,
        id: str,  # pylint: disable=redefined-builtin, invalid-name
        marks=(),
        places: typing.Any = DEFAULT_PLACES,
        logins: typing.Any = [{'login': 'a'}, {'login': 'b'}, {'login': 'w'}],
        has_line: typing.Any = True,
        response_status: typing.Any = 200,
        status_restapp: typing.Any = 200,
):
    return pytest.param(
        places,
        logins,
        has_line,
        response_status,
        status_restapp,
        id=id,
        marks=marks,
    )


@pytest.mark.config(
    EATS_AUTHORIZE_PERSONAL_MANAGER_SETTINGS={'logins_limit': 3},
)
@pytest.mark.pgsql('eats_authorize_personal_manager', files=['add_info.sql'])
@pytest.mark.parametrize(
    ('places', 'logins', 'has_line', 'response_status', 'status_restapp'),
    (
        make_pytest_param(id='success'),
        make_pytest_param(
            id='success2',
            places=[{'place_id': 321123, 'logins': ['a']}],
            logins=[{'login': 'a'}],
            has_line=False,
        ),
        make_pytest_param(
            id='wrong_quantity',
            places=[{'place_id': 123, 'logins': ['a', 'b', 'w', 'e']}],
            response_status=400,
        ),
        make_pytest_param(
            id='wrong_quantity',
            places=[{'place_id': 123, 'logins': ['a', 'b', 'w', 'e']}],
            response_status=403,
            status_restapp=403,
        ),
    ),
)
async def test_get_admin_acc(
        web_app_client,
        load_json,
        pgsql,
        eats_restapp_authorizer_mock,
        places,
        logins,
        has_line,
        response_status,
        status_restapp,
):

    response = await web_app_client.post(
        '/4.0/restapp-front/personal-manager/v1/telegram/bind',
        headers={'X-YaEda-PartnerId': '123'},
        json={'places': places},
    )
    assert response.status == response_status
    if response.status == 200:
        response_json = await response.json()
        assert response_json['meta']['logins_limit'] == 3
        assert response_json['payload'][0]['has_line'] == has_line
        assert response_json['payload'][0]['logins'] == logins
        assert _get_line_count(pgsql, places[0]['place_id']) == 1


def _get_line_count(pgsql, place_id):
    with pgsql['eats_authorize_personal_manager'].cursor() as cursor:
        cursor.execute(
            f'select count(*) from line_bind_place where place_id={place_id}',
        )
        count = list(row[0] for row in cursor)[0]
    return count
