import pytest

from tests_bank_applications import common

HANDLE_URL = '/applications-support/v1/get_filters_suggest'


async def test_get_filters_suggest_ok(
        taxi_bank_applications, mockserver, access_control_mock,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=common.get_support_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {
        'filters': [
            {'name': 'application_id', 'label': 'Идентификатор заявки'},
            {'name': 'uid', 'label': 'YandexUID'},
            {'name': 'buid', 'label': 'BankUID'},
            {'name': 'date_from', 'label': 'С времени'},
            {'name': 'date_to', 'label': 'По время'},
            {
                'name': 'type',
                'label': 'Тип заявки',
                'presets': [
                    {'key': 'REGISTRATION', 'value': 'Регистрация'},
                    {'key': 'SIMPLIFIED_IDENTIFICATION', 'value': 'УПРИД'},
                    {'key': 'DIGITAL_CARD_ISSUE', 'value': 'Цифровая карта'},
                    {'key': 'SPLIT_CARD_ISSUE', 'value': 'Карта Сплита'},
                    {'key': 'PRODUCT', 'value': 'Выпуск продукта'},
                    {'key': 'PLUS', 'value': 'Подписка Яндекс Плюс'},
                ],
            },
            {
                'name': 'status',
                'label': 'Статус заявки',
                'presets': [
                    {'key': 'CREATED', 'value': 'Созданная'},
                    {'key': 'PROCESSING', 'value': 'Обрабатываемая'},
                    {'key': 'FAILED', 'value': 'Проваленная'},
                    {'key': 'SUCCESS', 'value': 'Успешная'},
                ],
            },
        ],
    }
    assert access_control_mock.handler_path == HANDLE_URL


async def test_get_filters_suggest_access_deny(
        taxi_bank_applications, mockserver, access_control_mock,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=common.get_support_headers(''),
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1


@pytest.mark.config(BANK_ACCESS_CONTROL_ENABLE_CHECK=False)
async def test_get_filters_suggest_access_deny_but_config(
        taxi_bank_applications, mockserver, access_control_mock,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=common.get_support_headers(''),
    )
    assert response.status_code == 200
    assert access_control_mock.apply_policies_handler.times_called == 0
