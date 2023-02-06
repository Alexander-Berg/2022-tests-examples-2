import pytest

from tests_bank_userinfo import common

HANDLE_URL = '/userinfo-support/v1/get_filters_suggest'


async def test_get_filters_suggest_ok(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL, headers=common.get_support_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {
        'filters': [
            {'name': 'session_uuid', 'label': 'Идентификатор сессии'},
            {'name': 'uid', 'label': 'YandexUID'},
            {'name': 'buid', 'label': 'BankUID'},
            {'name': 'phone_id', 'label': 'BankPhoneID'},
            {'name': 'created_date_from', 'label': 'С времени создания'},
            {'name': 'created_date_to', 'label': 'По время создания'},
            {'name': 'updated_date_from', 'label': 'С времени обновления'},
            {'name': 'updated_date_to', 'label': 'По время обновления'},
            {
                'name': 'status',
                'label': 'Статус сессии',
                'presets': [
                    {
                        'key': 'account_recovery_required',
                        'value': 'Требуется восстановление аккаунта',
                    },
                    {
                        'key': 'app_update_required',
                        'value': 'Требуется обновление приложения',
                    },
                    {
                        'key': 'bank_phone_without_buid',
                        'value': 'BankPhoneId без пользователя',
                    },
                    {
                        'key': 'bank_risk_deny',
                        'value': 'Заблокирована антифродом',
                    },
                    {'key': 'banned', 'value': 'Забанена'},
                    {'key': 'fonish', 'value': 'Фониш'},
                    {
                        'key': 'invalid_token',
                        'value': 'Неверный токен паспорта',
                    },
                    {
                        'key': 'not_authorized',
                        'value': 'Не авторизован (требуется 2fa)',
                    },
                    {'key': 'not_registered', 'value': 'Не зарегистрирован'},
                    {'key': 'ok', 'value': 'OK'},
                    {
                        'key': 'phone_recovery_required',
                        'value': 'Требуется подтверждение номера',
                    },
                    {
                        'key': 'required_application_in_progress',
                        'value': 'Есть обязательные заявки к исполнению',
                    },
                ],
            },
        ],
    }
    assert access_control_mock.handler_path == HANDLE_URL


async def test_get_filters_suggest_access_deny(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL, headers=common.get_support_headers(''),
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1


@pytest.mark.config(BANK_ACCESS_CONTROL_ENABLE_CHECK=False)
async def test_get_filters_suggest_access_deny_but_config(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL, headers=common.get_support_headers(''),
    )
    assert response.status_code == 200
    assert access_control_mock.apply_policies_handler.times_called == 0
