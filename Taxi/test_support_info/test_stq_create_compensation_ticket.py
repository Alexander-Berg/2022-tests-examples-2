# pylint: disable=redefined-outer-name
import datetime

import pytest

from support_info import stq_task
from support_info.internal import stq_finance_ticket


@pytest.fixture
def mock_get_order(
        support_info_app_stq,
        patch_aiohttp_session,
        response_mock,
        order_archive_mock,
):
    archive_api_url = support_info_app_stq.settings.ARCHIVE_API_URL

    def _wrap(alias_id, order_data, order_proc_data):
        if order_proc_data:
            order_archive_mock.set_order_proc(order_proc_data)

        @patch_aiohttp_session(archive_api_url, 'POST')
        def _dummy_archive_api_request(method, url, **kwargs):
            assert kwargs['json']['id'] == alias_id
            assert url == archive_api_url + '/archive/order'
            if order_data:
                return response_mock(json={'doc': order_data})
            return response_mock(status=404)

        return _dummy_archive_api_request

    return _wrap


@pytest.mark.parametrize(
    'alias_id, order_data, order_proc_data, compensation_amount, comment,'
    'expected_create_ticket',
    [
        (
            'some_alias_id',
            {'_id': 'some_order_id'},
            {
                '_id': 'some_order_id',
                'order': {
                    'user_id': 'yandex_user_id',
                    'nz': 'moscow',
                    'request': {'due': datetime.datetime(2019, 1, 1, 0, 0)},
                    'performer': {
                        'uuid': 'driver_uuid',
                        'clid': '100500',
                        'db_id': 'some_park_id',
                        'taxi_alias': {'id': 'some_alias_id'},
                        'tariff': {'class': 'econom', 'id': 'some_tariff_id'},
                    },
                },
                'aliases': [{'id': 'some_alias_id'}],
            },
            '123',
            '456',
            {
                'queue': 'SUPPARTNERS',
                'summary': 'Компенсация по заказу some_order_id',
                'description': (
                    'Комментарий: 456\n'
                    'Название таксопарка: park_name\n'
                    'E-mail: some@email\n'
                    'CLID: 100500\n'
                    'ID поездки: some_alias_id\n'
                    'Номер водительского удостоверения: driver_license\n'
                    'Город: moscow\n'
                    'Дата поездки: 01.01 03:00\n'
                    'Тариф: some_tariff_id\n'
                    'Класс: econom\n'
                    'Сумма компенсации: 123\n'
                    'Заказ в админке Таксометра: '
                    '/redirect/to/order?db=some_park_id&order=some_order_id\n'
                    'Заказ в админке Такси: /orders/some_order_id'
                ),
                'tags': ['compensation_cost'],
                'custom_fields': {
                    'OrderId': 'some_order_id',
                    'driverPhone': '+791234',
                    'taximeterVersion': '7.07',
                    'driverLicense': 'driver_license',
                    'DriverUuid': 'driver_uuid',
                    'clid': '100500',
                    'parkDbId': 'some_park_id',
                    'ParkPhone': '+79123',
                    'parkName': 'park_name',
                    'parkEmail': 'some@email',
                    'country': 'rus',
                    'tariff': 'econom',
                    'orderDate': '01.01',
                    'orderTime': '03:00',
                    'coupon': 'False',
                    'couponUsed': 'False',
                    'appVersion': '3.8.1',
                    'userPlatform': 'iphone',
                    'emailFrom': 'some@email',
                    'emailTo': ['park@taxi.yandex.ru'],
                    'emailCreatedBy': 'park@taxi.yandex.ru',
                    'orderCost': '0',
                    'pointBChanged': 'False',
                    'waitingCost': '0',
                },
                'unique': 'compensation-ticket-some_order_id',
            },
        ),
        (
            'some_alias_id',
            {'_id': 'some_order_id'},
            {
                '_id': 'some_order_id',
                'order': {
                    'user_id': 'uber_user_id',
                    'nz': 'moscow',
                    'request': {'due': datetime.datetime(2019, 1, 1, 0, 0)},
                    'performer': {
                        'uuid': 'driver_uuid',
                        'clid': '100500',
                        'db_id': 'some_park_id',
                        'taxi_alias': {'id': 'some_alias_id'},
                        'tariff': {'class': 'econom', 'id': 'some_tariff_id'},
                    },
                },
                'aliases': [{'id': 'some_alias_id'}],
            },
            '123',
            '456',
            {
                'queue': 'SUPPARTNERS',
                'summary': 'Компенсация по заказу some_order_id',
                'description': (
                    'Комментарий: 456\n'
                    'Название таксопарка: park_name\n'
                    'E-mail: some@email\n'
                    'CLID: 100500\n'
                    'ID поездки: some_alias_id\n'
                    'Номер водительского удостоверения: driver_license\n'
                    'Город: moscow\n'
                    'Дата поездки: 01.01 03:00\n'
                    'Тариф: some_tariff_id\n'
                    'Класс: econom\n'
                    'Сумма компенсации: 123\n'
                    'Заказ в админке Таксометра: '
                    '/redirect/to/order?db=some_park_id&order=some_order_id\n'
                    'Заказ в админке Такси: /orders/some_order_id'
                ),
                'tags': ['compensation_cost'],
                'custom_fields': {
                    'OrderId': 'some_order_id',
                    'driverPhone': '+791234',
                    'taximeterVersion': '7.07',
                    'driverLicense': 'driver_license',
                    'DriverUuid': 'driver_uuid',
                    'clid': '100500',
                    'parkDbId': 'some_park_id',
                    'ParkPhone': '+79123',
                    'parkName': 'park_name',
                    'parkEmail': 'some@email',
                    'country': 'rus',
                    'tariff': 'econom',
                    'orderDate': '01.01',
                    'orderTime': '03:00',
                    'coupon': 'False',
                    'couponUsed': 'False',
                    'appVersion': '3.8.1',
                    'userPlatform': 'uber_android',
                    'emailFrom': 'some@email',
                    'emailTo': ['park@taxi.yandex.ru'],
                    'emailCreatedBy': 'park@taxi.yandex.ru',
                    'orderCost': '0',
                    'pointBChanged': 'False',
                    'waitingCost': '0',
                },
                'unique': 'compensation-ticket-some_order_id',
            },
        ),
        (
            'some_alias_id',
            {'_id': 'some_order_id'},
            {
                '_id': 'some_order_id',
                'order': {
                    'user_id': 'yandex_user_id',
                    'nz': 'paris',
                    'request': {'due': datetime.datetime(2019, 1, 1, 0, 0)},
                    'performer': {
                        'uuid': 'driver_uuid',
                        'clid': '100500',
                        'db_id': 'some_park_id',
                        'taxi_alias': {'id': 'some_alias_id'},
                        'tariff': {'class': 'econom', 'id': 'some_tariff_id'},
                    },
                },
                'aliases': [{'id': 'some_alias_id'}],
            },
            '123',
            '456',
            {
                'queue': 'INTL',
                'summary': 'Компенсация по заказу some_order_id',
                'description': (
                    'Комментарий: 456\n'
                    'Название таксопарка: park_name\n'
                    'E-mail: some@email\n'
                    'CLID: 100500\n'
                    'ID поездки: some_alias_id\n'
                    'Номер водительского удостоверения: driver_license\n'
                    'Город: moscow\n'
                    'Дата поездки: 01.01 03:00\n'
                    'Тариф: some_tariff_id\n'
                    'Класс: econom\n'
                    'Сумма компенсации: 123\n'
                    'Заказ в админке Таксометра: '
                    '/redirect/to/order?db=some_park_id&order=some_order_id\n'
                    'Заказ в админке Такси: /orders/some_order_id'
                ),
                'tags': ['compensation_cost'],
                'custom_fields': {
                    'OrderId': 'some_order_id',
                    'driverPhone': '+791234',
                    'taximeterVersion': '7.07',
                    'driverLicense': 'driver_license',
                    'DriverUuid': 'driver_uuid',
                    'clid': '100500',
                    'parkDbId': 'some_park_id',
                    'ParkPhone': '+79123',
                    'parkName': 'park_name',
                    'parkEmail': 'some@email',
                    'country': 'fra',
                    'tariff': 'econom',
                    'orderDate': '01.01',
                    'orderTime': '03:00',
                    'coupon': 'False',
                    'couponUsed': 'False',
                    'appVersion': '3.8.1',
                    'userPlatform': 'iphone',
                    'emailFrom': 'some@email',
                    'emailTo': ['support@taxi.yandex.ru'],
                    'emailCreatedBy': 'support@taxi.yandex.ru',
                    'orderCost': '0',
                    'pointBChanged': 'False',
                    'waitingCost': '0',
                },
                'unique': 'compensation-ticket-some_order_id',
            },
        ),
        (
            'some_alias_id',
            {'_id': 'some_order_id'},
            {
                '_id': 'some_order_id',
                'order': {
                    'user_id': 'uber_az_user_id',
                    'nz': 'baku',
                    'request': {'due': datetime.datetime(2019, 1, 1, 0, 0)},
                    'performer': {
                        'uuid': 'driver_uuid',
                        'clid': '100500',
                        'db_id': 'some_park_id',
                        'taxi_alias': {'id': 'some_alias_id'},
                        'tariff': {'class': 'econom', 'id': 'some_tariff_id'},
                    },
                },
                'aliases': [{'id': 'some_alias_id'}],
            },
            '123',
            '456',
            {
                'queue': 'UBER',
                'summary': 'Компенсация по заказу some_order_id',
                'description': (
                    'Комментарий: 456\n'
                    'Название таксопарка: park_name\n'
                    'E-mail: some@email\n'
                    'CLID: 100500\n'
                    'ID поездки: some_alias_id\n'
                    'Номер водительского удостоверения: driver_license\n'
                    'Город: moscow\n'
                    'Дата поездки: 01.01 03:00\n'
                    'Тариф: some_tariff_id\n'
                    'Класс: econom\n'
                    'Сумма компенсации: 123\n'
                    'Заказ в админке Таксометра: '
                    '/redirect/to/order?db=some_park_id&order=some_order_id\n'
                    'Заказ в админке Такси: /orders/some_order_id'
                ),
                'tags': ['compensation_cost'],
                'custom_fields': {
                    'OrderId': 'some_order_id',
                    'driverPhone': '+791234',
                    'taximeterVersion': '7.07',
                    'driverLicense': 'driver_license',
                    'DriverUuid': 'driver_uuid',
                    'clid': '100500',
                    'parkDbId': 'some_park_id',
                    'ParkPhone': '+79123',
                    'parkName': 'park_name',
                    'parkEmail': 'some@email',
                    'country': 'aze',
                    'tariff': 'econom',
                    'orderDate': '01.01',
                    'orderTime': '03:00',
                    'coupon': 'False',
                    'couponUsed': 'False',
                    'appVersion': '3.8.1',
                    'userPlatform': 'uber_android_az',
                    'emailFrom': 'some@email',
                    'emailTo': ['az@support-uber.com'],
                    'emailCreatedBy': 'az@support-uber.com',
                    'orderCost': '0',
                    'pointBChanged': 'False',
                    'waitingCost': '0',
                },
                'unique': 'compensation-ticket-some_order_id',
            },
        ),
        (
            'some_alias_id',
            {'_id': 'some_order_id'},
            {
                '_id': 'some_order_id',
                'order': {
                    'user_id': 'uber_fr_user_id',
                    'nz': 'paris',
                    'request': {'due': datetime.datetime(2019, 1, 1, 0, 0)},
                    'performer': {
                        'uuid': 'driver_uuid',
                        'clid': '100500',
                        'db_id': 'some_park_id',
                        'taxi_alias': {'id': 'some_alias_id'},
                        'tariff': {'class': 'econom', 'id': 'some_tariff_id'},
                    },
                },
                'aliases': [{'id': 'some_alias_id'}],
            },
            '123',
            '456',
            {
                'queue': 'SUPPORT',
                'summary': 'Компенсация по заказу some_order_id',
                'description': (
                    'Комментарий: 456\n'
                    'Название таксопарка: park_name\n'
                    'E-mail: some@email\n'
                    'CLID: 100500\n'
                    'ID поездки: some_alias_id\n'
                    'Номер водительского удостоверения: driver_license\n'
                    'Город: moscow\n'
                    'Дата поездки: 01.01 03:00\n'
                    'Тариф: some_tariff_id\n'
                    'Класс: econom\n'
                    'Сумма компенсации: 123\n'
                    'Заказ в админке Таксометра: '
                    '/redirect/to/order?db=some_park_id&order=some_order_id\n'
                    'Заказ в админке Такси: /orders/some_order_id'
                ),
                'tags': ['compensation_cost'],
                'custom_fields': {
                    'OrderId': 'some_order_id',
                    'driverPhone': '+791234',
                    'taximeterVersion': '7.07',
                    'driverLicense': 'driver_license',
                    'DriverUuid': 'driver_uuid',
                    'clid': '100500',
                    'parkDbId': 'some_park_id',
                    'ParkPhone': '+79123',
                    'parkName': 'park_name',
                    'parkEmail': 'some@email',
                    'country': 'fra',
                    'tariff': 'econom',
                    'orderDate': '01.01',
                    'orderTime': '03:00',
                    'coupon': 'False',
                    'couponUsed': 'False',
                    'emailFrom': 'some@email',
                    'appVersion': '3.8.1',
                    'userPlatform': 'uber_iphone_fr',
                    'emailTo': ['support@support-uber.com'],
                    'emailCreatedBy': 'support@support-uber.com',
                    'orderCost': '0',
                    'pointBChanged': 'False',
                    'waitingCost': '0',
                },
                'unique': 'compensation-ticket-some_order_id',
            },
        ),
        (
            'some_alias_id',
            {
                '_id': 'some_order_id',
                'calc': {
                    'allowed_tariffs': {'park_id': {'tariff_id': 234.0}},
                    'time': 250.0,
                    'distance': 5000.0,
                },
            },
            {
                '_id': 'some_order_id',
                'order': {
                    'user_id': 'yango_user_id',
                    'nz': 'paris',
                    'request': {'due': datetime.datetime(2019, 1, 1, 0, 0)},
                    'performer': {
                        'uuid': 'driver_uuid',
                        'clid': '100500',
                        'db_id': 'some_park_id',
                        'taxi_alias': {'id': 'some_alias_id'},
                        'tariff': {'class': 'econom', 'id': 'some_tariff_id'},
                    },
                },
                'aliases': [{'id': 'some_alias_id'}],
            },
            '123',
            '456',
            {
                'queue': 'INTL',
                'summary': 'Компенсация по заказу some_order_id',
                'description': (
                    'Комментарий: 456\n'
                    'Название таксопарка: park_name\n'
                    'E-mail: some@email\n'
                    'CLID: 100500\n'
                    'ID поездки: some_alias_id\n'
                    'Номер водительского удостоверения: driver_license\n'
                    'Город: moscow\n'
                    'Дата поездки: 01.01 03:00\n'
                    'Тариф: some_tariff_id\n'
                    'Класс: econom\n'
                    'Сумма компенсации: 123\n'
                    'Заказ в админке Таксометра: '
                    '/redirect/to/order?db=some_park_id&order=some_order_id\n'
                    'Заказ в админке Такси: /orders/some_order_id'
                ),
                'tags': ['compensation_cost'],
                'custom_fields': {
                    'OrderId': 'some_order_id',
                    'driverPhone': '+791234',
                    'taximeterVersion': '7.07',
                    'driverLicense': 'driver_license',
                    'DriverUuid': 'driver_uuid',
                    'clid': '100500',
                    'parkDbId': 'some_park_id',
                    'ParkPhone': '+79123',
                    'parkName': 'park_name',
                    'parkEmail': 'some@email',
                    'country': 'fra',
                    'tariff': 'econom',
                    'orderDate': '01.01',
                    'orderTime': '03:00',
                    'coupon': 'False',
                    'couponUsed': 'False',
                    'appVersion': '3.8.1',
                    'userPlatform': 'yango_iphone',
                    'emailFrom': 'some@email',
                    'emailTo': ['support@yango.yandex.com'],
                    'emailCreatedBy': 'support@yango.yandex.com',
                    'orderCost': '0',
                    'pointBChanged': 'False',
                    'waitingCost': '0',
                },
                'unique': 'compensation-ticket-some_order_id',
            },
        ),
    ],
)
async def test_create_compensation_ticket(
        support_info_app_stq,
        mock_get_order,
        mock_st_create_ticket,
        mock_get_users,
        mock_personal,
        mock_driver_profiles,
        mock_driver_trackstory,
        mock_driver_priority,
        mock_persey_payments,
        mock_taxi_fleet,
        alias_id,
        order_data,
        order_proc_data,
        compensation_amount,
        comment,
        expected_create_ticket,
):
    mock_get_order(alias_id, order_data, order_proc_data)
    await stq_task.create_compensation_ticket(
        support_info_app_stq, alias_id, compensation_amount, comment,
    )
    create_ticket_kwargs = mock_st_create_ticket.calls[0]['kwargs']
    assert create_ticket_kwargs == expected_create_ticket


@pytest.mark.config(STARTRACK_FINANCE_TICKET_RULES=[])
@pytest.mark.parametrize(
    'alias_id, order_data, order_proc_data, compensation_amount, comment',
    [
        (
            'some_alias_id',
            {'_id': 'some_order_id'},
            {
                '_id': 'some_order_id',
                'order': {
                    'user_id': 'yandex_user_id',
                    'nz': 'moscow',
                    'request': {'due': datetime.datetime(2019, 1, 1, 0, 0)},
                    'performer': {
                        'uuid': 'driver_uuid',
                        'clid': '100500',
                        'taxi_alias': {'id': 'some_alias_id'},
                        'tariff': {'class': 'econom', 'id': 'some_tariff_id'},
                    },
                },
            },
            '123',
            '456',
        ),
    ],
)
async def test_no_matching_rules(
        support_info_app_stq,
        mock_get_order,
        mock_personal,
        alias_id,
        order_data,
        order_proc_data,
        compensation_amount,
        comment,
):
    mock_get_order(alias_id, order_data, order_proc_data)
    with pytest.raises(stq_finance_ticket.CannotCreateFinanceTicket):
        await stq_task.create_compensation_ticket(
            support_info_app_stq, alias_id, compensation_amount, comment,
        )
