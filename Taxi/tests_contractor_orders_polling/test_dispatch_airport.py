import pytest

from tests_contractor_orders_polling import utils


TAXIMETER_MESSAGES = {
    'airportqueue.exact_time': {
        'ru': '%(minutes)s мин',
        'en': '%(minutes)s min',
    },
    'airportqueue.exact_time_hours': {
        'ru': '%(hours)s ч',
        'en': '%(hours)s h',
    },
    'airportqueue.exact_time_hours_minutes': {
        'ru': '%(hours)s ч %(minutes)s мин',
        'en': '%(hours)s h %(minutes)s min',
    },
    'airportqueue.estimated_time_more_hours': {
        'ru': 'Более %(hours)s ч',
        'en': 'More than %(hours)s h',
    },
    'airportqueue.estimated_time_less_minutes': {
        'ru': 'Менее %(minutes)s мин',
        'en': 'Less than %(minutes)s min',
    },
    'airport_tanker_key': {'ru': 'ЕКБ', 'en': 'EKB'},
    'text_tanker_key': {'ru': 'Текст', 'en': 'Text'},
    'title_tanker_key': {'ru': 'Заголовок', 'en': 'Title'},
    'queue_title_tanker_key': {'ru': 'Очередь', 'en': 'Queue'},
    'ok_key': {'ru': 'Да', 'en': 'Yes'},
    'no_key': {'ru': 'Нет', 'en': 'No'},
    'airportqueue.position': {'ru': '%(place_min)s-%(place_max)s'},
    'airportqueue.position.theone': {'ru': '%(place_exact)s'},
}

TARIFF_MESSAGES = {
    'car_category_econom': {'ru': 'Эконом', 'en': 'Econom'},
    'car_category_business': {'ru': 'Комфорт', 'en': 'Comfort'},
    'car_category_comfortplus': {'ru': 'Комфорт+', 'en': 'Comfort+'},
}


async def test_dispatch_airports_cache(
        taxi_contractor_orders_polling, mockserver, load_json,
):
    @mockserver.json_handler('dispatch-airport/v1/info/drivers')
    def _dispatch_airport_handler(request):
        return load_json('dispatch_airport_response.json')

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers={**utils.HEADERS, 'X-YaTaxi-Driver-Profile-Id': 'uuid1'},
        params={'md5_queueinfo_v2': ''},
    )

    assert response.status_code == 200
    # TODO test removing of a driver from cache
    # assert response.json().get('md5_queueinfo_v2') == ''
    # assert response.json().get('queueinfo_v2') == {}


async def test_dispatch_airports_cache_failed_request(
        taxi_contractor_orders_polling, mockserver, load_json,
):
    @mockserver.handler('dispatch-airport/v1/info/drivers')
    def _dispatch_airport_handler(request):
        return mockserver.make_response(status=500)

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers={**utils.HEADERS, 'X-YaTaxi-Driver-Profile-Id': 'unknown'},
        params={'md5_queueinfo_v2': ''},
    )

    assert response.status_code == 200


async def test_dispatch_airports_unknown_driver(
        taxi_contractor_orders_polling, mockserver,
):
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers={**utils.HEADERS, 'X-YaTaxi-Driver-Profile-Id': 'unknown'},
        params={'md5_queueinfo_v2': ''},
    )

    assert response.status_code == 200
    assert 'md5_queueinfo_v2' not in response.json()


@pytest.mark.translations(taximeter_messages=TAXIMETER_MESSAGES)
@pytest.mark.parametrize('waiting_time_exists', [True, False])
async def test_request_dispatch_airport_queue_info_v2_near(
        taxi_contractor_orders_polling,
        mockserver,
        load_json,
        waiting_time_exists,
):
    @mockserver.json_handler('dispatch-airport/v1/info/drivers')
    def _mock_dispatch_airport(request):
        return load_json('dispatch_airport_response.json')

    uuid = 'uuid1' if waiting_time_exists else 'uuid4'
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers={**utils.HEADERS, 'X-YaTaxi-Driver-Profile-Id': uuid},
        params={'md5_queueinfo_v2': ''},
    )
    assert response.status_code == 200
    response_obj = response.json()

    assert 'md5_queueinfo_v2' in response_obj
    etalon = {
        'active': [],
        'dialog_events': [
            {'dialog': 'test_dialog_id', 'from': 'near', 'to': 'in'},
            {'dialog': 'test_dialog_id1', 'to': 'out'},
        ],
        'dialogs': [
            {
                'affirmative_button': 'Да',
                'name': 'test_dialog_id',
                'negative_button': 'Нет',
                'text': 'Текст',
                'title': 'Заголовок',
                'type': 'modal_window_2',
                'severity': 'info',
            },
            {
                'affirmative_button': 'Да',
                'name': 'test_dialog_id1',
                'negative_button': 'Нет',
                'text': 'Текст',
                'title': 'Заголовок',
                'type': 'alert',
                'severity': 'info',
            },
        ],
        'near': [
            {
                'icon_id': 'airport',
                'airport_title': 'ЕКБ',
                'queue_title': 'Очередь',
                'region_name': 'ekb_airport_notification',
                'show_navigation_button': False,
                'options': {
                    'line_color': '#169CDC',
                    'fill_color': '#48169CDC',
                },
            },
        ],
        'dialog_state': 'near',
    }
    if waiting_time_exists:
        etalon['near'][0]['queue_exact_time'] = 'Менее 5 мин'
    assert response_obj['queueinfo_v2'] == etalon


@pytest.mark.translations(
    taximeter_messages=TAXIMETER_MESSAGES,
    taximeter_backend_driver_messages=TARIFF_MESSAGES,
)
@pytest.mark.config(
    DISPATCH_AIRPORT_ZONES={
        'ekb': {
            'airport_title_key': 'ekb_airport_key',
            'enabled': True,
            'main_area': 'ekb_airport',
            'notification_area': 'ekb_airport_notification',
            'old_mode_enabled': True,
            'tariff_home_zone': 'ekb',
            'update_interval_sec': 1,
            'use_queue': False,
            'waiting_area': 'ekb_airport_waiting',
            'whitelist_classes': {},
        },
    },
)
async def test_request_dispatch_airport_queue_dont_use(
        taxi_contractor_orders_polling, mockserver, load_json,
):
    @mockserver.json_handler('dispatch-airport/v1/info/drivers')
    def _mock_dispatch_airport(request):
        return load_json('dispatch_airport_response.json')

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers={**utils.HEADERS, 'X-YaTaxi-Driver-Profile-Id': 'uuid2'},
        params={'md5_queueinfo_v2': ''},
    )
    assert response.status_code == 200
    assert 'md5_queueinfo_v2' not in response.json()


@pytest.mark.translations(
    taximeter_messages=TAXIMETER_MESSAGES,
    taximeter_backend_driver_messages=TARIFF_MESSAGES,
)
async def test_request_dispatch_airport_queue_info_v2_active(
        taxi_contractor_orders_polling, mockserver, load_json,
):
    @mockserver.json_handler('dispatch-airport/v1/info/drivers')
    def _mock_dispatch_airport(request):
        return load_json('dispatch_airport_response.json')

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers={
            **utils.HEADERS,
            'X-YaTaxi-Driver-Profile-Id': 'uuid2',
            'Accept-Language': 'en-US',
        },
        params={'md5_queueinfo_v2': ''},
    )
    assert response.status_code == 200
    response_obj = response.json()

    assert 'md5_queueinfo_v2' in response_obj
    assert response_obj['queueinfo_v2'] == {
        'active': [
            {
                'icon_id': 'airport',
                'airport_title': 'EKB',
                'current_place': '16-20',
                'queue_exact_time': '1 h',
                'queue_title': 'Queue',
                'options': {
                    'line_color': '#169CDC',
                    'fill_color': '#48169CDC',
                },
                'queues_infos': [
                    {
                        'current_place': '16-20',
                        'category_name': 'Econom',
                        'category_key': 'econom',
                        'queue_exact_time': '1 h',
                        'class_code': 1,
                    },
                    {
                        'current_place': '21-25',
                        'queue_exact_time': '1 h 30 min',
                        'class_code': 4,
                        'category_name': 'Comfort',
                        'category_key': 'business',
                    },
                    {
                        'current_place': '21-25',
                        'queue_exact_time': 'More than 2 h',
                        'class_code': 512,
                        'category_name': 'Comfort+',
                        'category_key': 'comfortplus',
                    },
                ],
                'region_name': 'ekb_airport_waiting',
                'show_details_button': True,
                'show_navigation_button': False,
                'timeout_due': 1622937600,
            },
        ],
        'dialog_events': [
            {'dialog': 'test_dialog_id1', 'from': 'in', 'to': 'out'},
        ],
        'dialogs': [
            {
                'affirmative_button': 'Yes',
                'name': 'test_dialog_id1',
                'negative_button': 'No',
                'text': 'Text',
                'type': 'alert',
                'severity': 'info',
            },
        ],
        'near': [],
        'dialog_state': 'in',
    }


@pytest.mark.translations(
    taximeter_messages=TAXIMETER_MESSAGES,
    taximeter_backend_driver_messages=TARIFF_MESSAGES,
)
async def test_request_dispatch_airport_queue_info_v2_active_unavailable(
        taxi_contractor_orders_polling, mockserver, load_json,
):
    @mockserver.json_handler('dispatch-airport/v1/info/drivers')
    def _mock_dispatch_airport(request):
        return load_json('dispatch_airport_response.json')

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers={
            **utils.HEADERS,
            'X-YaTaxi-Driver-Profile-Id': 'uuid6',
            'Accept-Language': 'en-US',
        },
        params={'md5_queueinfo_v2': ''},
    )
    assert response.status_code == 200
    response_obj = response.json()

    assert 'md5_queueinfo_v2' in response_obj
    assert response_obj['queueinfo_v2'] == {
        'active': [
            {
                'icon_id': 'airport',
                'airport_title': 'EKB',
                'queue_title': 'Queue',
                'options': {
                    'line_color': '#FA3E2C',
                    'fill_color': '#14FA3E2C',
                },
                'queues_infos': [],
                'region_name': 'ekb_airport_waiting',
                'show_details_button': False,
                'show_navigation_button': False,
                'timeout_due': 1622938600,
            },
        ],
        'dialog_events': [
            {'dialog': 'test_dialog_id1', 'from': 'in', 'to': 'out'},
        ],
        'dialogs': [
            {
                'affirmative_button': 'Yes',
                'name': 'test_dialog_id1',
                'negative_button': 'No',
                'text': 'Text',
                'title': 'Title',
                'type': 'alert',
                'severity': 'info',
            },
        ],
        'near': [],
        'dialog_state': 'out',
    }


@pytest.mark.translations(
    taximeter_messages=TAXIMETER_MESSAGES,
    taximeter_backend_driver_messages=TARIFF_MESSAGES,
)
@pytest.mark.parametrize('waiting_time_exists', [True, False])
async def test_request_dispatch_airport_queue_info_v2_one_active(
        taxi_contractor_orders_polling,
        mockserver,
        load_json,
        waiting_time_exists,
):
    uuid = 'uuid3' if waiting_time_exists else 'uuid5'

    @mockserver.json_handler('dispatch-airport/v1/info/drivers')
    def _mock_dispatch_airport(request):
        return load_json('dispatch_airport_response.json')

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers={
            **utils.HEADERS,
            'X-YaTaxi-Driver-Profile-Id': uuid,
            'Accept-Language': 'en-US',
        },
        params={'md5_queueinfo_v2': ''},
    )
    assert response.status_code == 200
    response_obj = response.json()

    assert 'md5_queueinfo_v2' in response_obj
    etalon = {
        'active': [
            {
                'icon_id': 'airport',
                'airport_title': 'EKB',
                'current_place': '6-10',
                'queue_exact_time': '15 min',
                'queue_title': 'Queue',
                'queues_infos': [
                    {
                        'current_place': '6-10',
                        'queue_exact_time': '15 min',
                        'class_code': 1,
                        'category_name': 'Econom',
                        'category_key': 'econom',
                    },
                ],
                'region_name': 'ekb_airport_waiting',
                'show_details_button': False,
                'show_navigation_button': False,
                'timeout_due': 1622938600,
                'options': {
                    'line_color': '#169CDC',
                    'fill_color': '#48169CDC',
                },
            },
        ],
        'dialog_events': [
            {'dialog': 'test_dialog_id1', 'from': 'in', 'to': 'out'},
        ],
        'dialogs': [
            {
                'affirmative_button': 'Yes',
                'name': 'test_dialog_id1',
                'negative_button': 'No',
                'text': 'Text',
                'title': 'Title',
                'type': 'alert',
                'severity': 'info',
            },
        ],
        'near': [],
        'dialog_state': 'in',
    }
    if not waiting_time_exists:
        active_zone = etalon['active'][0]
        del active_zone['queue_exact_time']
        del active_zone['queues_infos'][0]['queue_exact_time']

    assert response_obj['queueinfo_v2'] == etalon

    # repeat request. check md5
    md5_queueinfo_v2 = response_obj['md5_queueinfo_v2']

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers={
            **utils.HEADERS,
            'X-YaTaxi-Driver-Profile-Id': uuid,
            'Accept-Language': 'en-US',
        },
        params={'md5_queueinfo_v2': md5_queueinfo_v2},
    )
    assert response.status_code == 200
    response_obj = response.json()

    assert 'md5_queueinfo_v2' in response_obj
    assert 'queueinfo_v2' not in response_obj
