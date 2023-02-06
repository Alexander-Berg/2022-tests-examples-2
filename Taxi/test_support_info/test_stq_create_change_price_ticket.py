# pylint: disable=redefined-outer-name
import datetime

import pytest

from support_info import stq_task


@pytest.fixture
def mock_get_order(
        support_info_app_stq,
        patch_aiohttp_session,
        response_mock,
        order_archive_mock,
):
    archive_api_url = support_info_app_stq.settings.ARCHIVE_API_URL

    def _wrap(order_id, order_data, order_proc_data):
        if order_proc_data:
            order_archive_mock.set_order_proc(order_proc_data)

        @patch_aiohttp_session(archive_api_url, 'POST')
        def _dummy_archive_api_request(method, url, **kwargs):
            assert kwargs['json']['id'] == order_id
            assert url == archive_api_url + '/archive/order'
            if order_data:
                return response_mock(json={'doc': order_data})
            return response_mock(status=404)

        return _dummy_archive_api_request

    return _wrap


@pytest.mark.parametrize('support_tags_enabled', [False, True])
@pytest.mark.config(
    SUPPORT_INFO_EXTERNAL_META_QUERIES=True,
    SUPPORT_INFO_CHATTERBOX_TAGS_SEARCH=False,
    SUPPORT_INFO_FETCH_EXTERNAL_TAGS=True,
    SUPPORT_INFO_TAG_USE_ZENDESK=False,
)
@pytest.mark.parametrize(
    'order_id, order_data, order_proc_data, expected_create_ticket',
    [
        (
            'some_order_id',
            {'_id': 'some_order_id'},
            {
                '_id': 'some_order_id',
                'order': {
                    'user_id': 'yandex_user_id',
                    'nz': 'moscow',
                    'request': {
                        'due': datetime.datetime(2019, 1, 1, 0, 0),
                        'source': {'fullname': 'source point'},
                        'destinations': [{'fullname': 'destination point'}],
                    },
                    'performer': {
                        'uuid': 'driver_uuid',
                        'clid': '100500',
                        'taxi_alias': {'id': 'some_alias_id'},
                        'tariff': {
                            'class': 'econom',
                            'id': 'some_tariff_id',
                            'currency': 'RUB',
                        },
                        'db_id': 'some_park_id',
                    },
                    'disp_cost': {'disp_cost': 123, 'taximeter_cost': 456},
                },
            },
            {
                'queue': 'SUPPARTNERS',
                'summary': (
                    'Заявка диспетчера на изменение стоимости заказа '
                    'some_order_id'
                ),
                'description': (
                    'ID заказа some_order_id\n'
                    'Сумма, на которую заказ закрыт фактически: '
                    '456 RUB\n'
                    'Сумма, которую выставил диспетчер: 123 RUB\n'
                    'Категория заказа: econom\n'
                    'Точка А: source point\n'
                    'Точка Б: destination point\n'
                    'Водительское удостоверение: driver_license\n'
                    'Заказ в админке Таксометра: '
                    '/redirect/to/order?db=some_park_id&order=some_order_id\n'
                    'Заказ в админке Такси: /orders/some_order_id'
                ),
                'tags': ['disp_change_cost'],
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
                    'pointA': 'source point',
                    'pointsB': 'destination point',
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
                'unique': 'dispatcher_change_price-ticket-some_order_id',
            },
        ),
        (
            'some_order_id',
            {'_id': 'some_order_id'},
            {
                '_id': 'some_order_id',
                'order': {
                    'user_id': 'uber_user_id',
                    'nz': 'paris',
                    'request': {
                        'due': datetime.datetime(2019, 1, 1, 0, 0),
                        'source': {'fullname': 'source point'},
                        'destinations': [{'fullname': 'destination point'}],
                    },
                    'performer': {
                        'uuid': 'driver_uuid',
                        'clid': '100500',
                        'taxi_alias': {'id': 'some_alias_id'},
                        'tariff': {
                            'class': 'econom',
                            'id': 'some_tariff_id',
                            'currency': 'RUB',
                        },
                        'db_id': 'some_park_id',
                    },
                    'disp_cost': {'driver_cost': 123, 'taximeter_cost': 456},
                },
            },
            {
                'queue': 'SUPPORT',
                'summary': (
                    'Заявка водителя на изменение стоимости заказа '
                    'some_order_id'
                ),
                'description': (
                    'ID заказа some_order_id\n'
                    'Сумма, на которую заказ закрыт фактически: '
                    '456 RUB\n'
                    'Сумма, которую выставил водитель: 123 RUB\n'
                    'Категория заказа: econom\n'
                    'Точка А: source point\n'
                    'Точка Б: destination point\n'
                    'Водительское удостоверение: driver_license\n'
                    'Заказ в админке Таксометра: '
                    '/redirect/to/order?db=some_park_id&order=some_order_id\n'
                    'Заказ в админке Такси: /orders/some_order_id'
                ),
                'tags': ['driver_change_cost'],
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
                    'pointA': 'source point',
                    'pointsB': 'destination point',
                    'country': 'fra',
                    'tariff': 'econom',
                    'orderDate': '01.01',
                    'orderTime': '03:00',
                    'coupon': 'False',
                    'couponUsed': 'False',
                    'appVersion': '3.8.1',
                    'userPlatform': 'uber_android',
                    'emailFrom': 'some@email',
                    'emailTo': ['support@support-uber.com'],
                    'emailCreatedBy': 'support@support-uber.com',
                    'orderCost': '0',
                    'pointBChanged': 'False',
                    'waitingCost': '0',
                },
                'unique': 'driver_change_price-ticket-some_order_id',
            },
        ),
    ],
)
async def test_create_change_price_ticket(
        support_info_app_stq,
        mock_get_order,
        mock_st_create_ticket,
        mock_get_users,
        mock_personal,
        mock_chatterbox_search,
        mock_support_tags,
        mock_driver_profiles,
        mock_driver_trackstory,
        mock_driver_priority,
        mock_persey_payments,
        mock_taxi_fleet,
        order_id,
        order_data,
        order_proc_data,
        expected_create_ticket,
        support_tags_enabled,
):
    mock_support_tags({'tags': []})
    support_info_app_stq.config.SUPPORT_INFO_FETCH_SUPPORT_TAGS = (
        support_tags_enabled
    )
    mock_get_order(order_id, order_data, order_proc_data)
    await stq_task.create_change_price_ticket(support_info_app_stq, order_id)
    create_ticket_kwargs = mock_st_create_ticket.calls[0]['kwargs']
    assert create_ticket_kwargs == expected_create_ticket
