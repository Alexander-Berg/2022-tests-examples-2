import pytest

from tests_bank_communications import common

COMMUNICATIONS_HANDLE_URL = (
    '/communications-support/v1/communications/get_filters_suggest'
)
SUBSCRIPTIONS_HANDLE_URL = (
    '/communications-support/v1/push_subscriptions/get_filters_suggest'
)


async def test_get_filters_suggest_ok(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        COMMUNICATIONS_HANDLE_URL, headers=common.get_support_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {
        'filters': [
            {
                'name': 'communication_id',
                'label': 'Идентификатор коммуникации',
            },
            {'name': 'buid', 'label': 'BankUID'},
            {'name': 'created_date_from', 'label': 'С времени создания'},
            {'name': 'created_date_to', 'label': 'По время создания'},
        ],
    }
    assert access_control_mock.handler_path == COMMUNICATIONS_HANDLE_URL


async def test_get_filters_suggest_access_deny(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        COMMUNICATIONS_HANDLE_URL, headers=common.get_support_headers(''),
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1


@pytest.mark.config(BANK_ACCESS_CONTROL_ENABLE_CHECK=False)
async def test_get_filters_suggest_access_deny_but_config(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        COMMUNICATIONS_HANDLE_URL, headers=common.get_support_headers(''),
    )
    assert response.status_code == 200
    assert access_control_mock.apply_policies_handler.times_called == 0


async def test_get_filters_suggest_push_subscriptions_ok(
        taxi_bank_communications, mockserver, access_control_mock,
):
    response = await taxi_bank_communications.post(
        SUBSCRIPTIONS_HANDLE_URL, headers=common.get_support_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {
        'filters': [
            {'name': 'subscription_id', 'label': 'Идентификатор подписки'},
            {'name': 'buid', 'label': 'BankUID'},
            {'name': 'created_date_from', 'label': 'С времени создания'},
            {'name': 'created_date_to', 'label': 'По время создания'},
            {'name': 'updated_date_from', 'label': 'С времени обновления'},
            {'name': 'updated_date_to', 'label': 'По время обновления'},
            {
                'name': 'status',
                'label': 'Статус подписки',
                'presets': [
                    {'key': 'ACTIVE', 'value': 'Активная'},
                    {'key': 'INACTIVE', 'value': 'Неактивная'},
                ],
            },
        ],
    }
