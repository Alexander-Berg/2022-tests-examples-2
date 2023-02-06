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
        disabled_ids: typing.Any = [],
        login: typing.Any = 'a',
        line: typing.Any = 'a',
):
    return pytest.param(
        place_ids, disabled_ids, login, line, id=id, marks=marks,
    )


@pytest.mark.pgsql('eats_authorize_personal_manager', files=['add_info.sql'])
@pytest.mark.parametrize(
    ('place_ids', 'disabled_ids', 'login', 'line'),
    (
        make_pytest_param(id='success'),
        make_pytest_param(
            id='success2', login='unique', line='', place_ids=[],
        ),
    ),
)
async def test_get_admin_acc(
        web_app_client,
        load_json,
        eats_place_subscriptions_mock,
        mock_personal,
        place_ids,
        disabled_ids,
        login,
        line,
):
    @mock_personal('/v1/telegram_logins/retrieve')
    async def _mock_login(request):
        return {'id': 'login_pd_id', 'value': login}

    response = await web_app_client.post(
        '/v1/get-chatterbox-places-authorize',
        json={'metadata': {'login_pd_id': 'login_pd_id'}},
    )
    response_json = await response.json()
    assert response_json['metadata']['place_ids'] == place_ids
    assert response_json['metadata']['login'] == login
    assert response_json['metadata']['line'] == line
