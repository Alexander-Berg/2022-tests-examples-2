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
        place_ids: typing.Any = [DEFAULT_PLACE_ID],
        disabled_ids: typing.Any = [],
        logins: typing.Any = ['q', 'w', 'e'],
        response_status: typing.Any = 204,
):
    return pytest.param(
        place_id,
        place_ids,
        disabled_ids,
        logins,
        response_status,
        id=id,
        marks=marks,
    )


@pytest.mark.config(
    EATS_AUTHORIZE_PERSONAL_MANAGER_SETTINGS={'logins_limit': 3},
)
@pytest.mark.pgsql('eats_authorize_personal_manager', files=['add_info.sql'])
@pytest.mark.parametrize(
    ('place_id', 'place_ids', 'disabled_ids', 'logins', 'response_status'),
    (
        make_pytest_param(id='success'),
        make_pytest_param(
            id='worng_size', logins=['a', 'b', 'd', 'c'], response_status=400,
        ),
        make_pytest_param(id='success_with_del', logins=['a', 'b']),
        # make_pytest_param(
        #     id='permission_den', place_ids=[],
        #     disabled_ids=[DEFAULT_PLACE_ID], response_status=400,
        # ),
    ),
)
async def test_get_admin_acc(
        web_app_client,
        eats_place_subscriptions_mock,
        pgsql,
        load_json,
        place_id,
        place_ids,
        disabled_ids,
        logins,
        response_status,
):
    response = await web_app_client.post(
        '/admin/v1/telegram/bind',
        json={'place_id': place_id, 'logins': logins},
    )
    assert response.status == response_status
    if response.status == 204:
        assert _get_count(pgsql, place_id) == len(logins)
        assert _get_line_count(pgsql, place_id) == 1


def _get_count(pgsql, place_id):
    with pgsql['eats_authorize_personal_manager'].cursor() as cursor:
        cursor.execute(
            f'select count(*) from login_bind_place where place_id={place_id}',
        )
        count = list(row[0] for row in cursor)[0]
    return count


def _get_line_count(pgsql, place_id):
    with pgsql['eats_authorize_personal_manager'].cursor() as cursor:
        cursor.execute(
            f'select count(*) from line_bind_place where place_id={place_id}',
        )
        count = list(row[0] for row in cursor)[0]
    return count
