import pytest

from tests_bank_authorization import common

HANDLE_URL = '/authorization-support/v1/get_filters_suggest'


async def test_get_filters_suggest_ok(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    response = await taxi_bank_authorization.post(
        HANDLE_URL, headers=common.get_support_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {
        'filters': [
            {'name': 'track_id', 'label': 'Идентификатор трека'},
            {'name': 'buid', 'label': 'BankUID'},
            {
                'name': 'operation_type',
                'label': 'Тип операции запроса авторизации',
            },
            {'name': 'created_date_from', 'label': 'С времени создания'},
            {'name': 'created_date_to', 'label': 'По время создания'},
            {'name': 'updated_date_from', 'label': 'С времени обновления'},
            {'name': 'updated_date_to', 'label': 'По время обновления'},
        ],
    }
    assert access_control_mock.apply_policies_handler.times_called == 1
    assert access_control_mock.handler_path == HANDLE_URL


async def test_get_filters_suggest_access_deny(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    response = await taxi_bank_authorization.post(
        HANDLE_URL, headers=common.get_support_headers(''),
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1


@pytest.mark.config(BANK_ACCESS_CONTROL_ENABLE_CHECK=False)
async def test_get_filters_suggest_access_deny_but_config(
        taxi_bank_authorization, mockserver, access_control_mock,
):
    response = await taxi_bank_authorization.post(
        HANDLE_URL, headers=common.get_support_headers(''),
    )
    assert response.status_code == 200
    assert access_control_mock.apply_policies_handler.times_called == 0
