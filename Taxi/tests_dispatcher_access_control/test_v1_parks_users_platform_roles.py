import pytest

from tests_dispatcher_access_control import utils

ENDPOINT = '/v1/parks/users/platform/roles'


@pytest.mark.redis_store(
    ['sadd', 'admin:rolemembers:Admin', 'admin@yandex.ru'],
    ['sadd', 'admin:rolemembers:Basic', 'user@yandex.ru'],
    ['sadd', 'admin:rolemembers:RegionalManager', 'user@yandex.ru'],
)
@pytest.mark.parametrize(
    'user_mail, user_roles',
    [
        ('admin@yandex.ru', ['Admin']),
        ('user@yandex.ru', ['Basic', 'RegionalManager']),
        ('user1@yandex.ru', []),
    ],
)
async def test_success(
        taxi_dispatcher_access_control,
        user_mail,
        user_roles,
        blackbox_service,
):
    blackbox_service.set_user_ticket_info('valid_ticket', '100', user_mail)
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT,
        headers={
            'X-Ya-User-Ticket': 'valid_ticket',
            'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body['roles'] == user_roles


async def test_failed_no_info_from_bb(
        taxi_dispatcher_access_control, blackbox_service,
):
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT,
        headers={
            'X-Ya-User-Ticket': 'valid_ticket',
            'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
        },
    )

    assert response.status_code == 400
