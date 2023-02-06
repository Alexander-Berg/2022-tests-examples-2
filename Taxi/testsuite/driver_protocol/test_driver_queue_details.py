import pytest

TAXIMETER_MESSAGES = {
    'airportqueue.details.text_minutes_template': {
        'ru': 'Ждать %(minutes)s мин, место: %(place)s',
    },
    'airportqueue.details.text_hours_template': {
        'ru': 'Ждать %(hours)s ч, место: %(place)s',
    },
    'airportqueue.details.text_hours_minutes_template': {
        'ru': 'Ждать %(hours)s ч %(minutes)s мин, место: %(place)s',
    },
    'airportqueue.details.text_more_hours_template': {
        'ru': 'Ждать более %(hours)s ч, место: %(place)s',
    },
    'airportqueue.details.text_less_minutes_template': {
        'ru': 'Ждать менее %(minutes)s мин, место: %(place)s',
    },
    'airportqueue.details.text_no_timeinfo_template': {
        'ru': 'Место: %(place)s',
    },
}

TARIFF_MESSAGES = {
    'old_category_name.econom': {'ru': 'Эконом', 'en': 'Econom'},
    'old_category_name.business': {'ru': 'Комфорт', 'en': 'Comfort'},
    'old_category_name.minivan': {'ru': 'Минивэн', 'en': 'Minivan'},
    'old_category_name.universal': {'ru': 'Универсал', 'en': 'Universal'},
    'old_category_name.comfortplus': {'ru': 'Комфорт+', 'en': 'Comfort+'},
    'old_category_name.express': {'ru': 'Экспресс', 'en': 'Express'},
}


@pytest.mark.redis_store(
    ['set', 'AirportQueue:Zone:777:888', 'rostovondon_airport'],
)
@pytest.mark.config(
    AIRPORT_QUEUE_SETTINGS={
        'rostovondon_airport': {
            'USE_NEW_MESSAGES': True,
            'MAX_MINUTES_BOUNDARY': 240,
        },
    },
    AIRPORT_QUEUE_MAX_WAITING_TIME_TO_SHOW_MINUTES=20 * 60,
)
@pytest.mark.filldb(queue_waiting_times='long')
def test_queue_details_more_than_2_hours(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'qwerty', '888')

    @mockserver.json_handler('/tracker/1.0/airport-queue-info')
    def mock_tracker(request):
        return {
            'status': 'in',
            'rejects_count': 1,
            'queues': [
                {
                    'enabled': True,
                    'queue_count': 10,
                    'position': 3,
                    'class_name': 'econom',
                },
            ],
        }

    response = taxi_driver_protocol.get(
        'driver/queue/details?db=777&session=qwerty'
        '&zone_id=rostovondon_airport',
        headers={'Accept-Language': 'ru-RU'},
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['description']
    queues = response_obj['queues']
    assert len(queues) == 1
    queue_econom = queues[0]
    assert queue_econom['text'] == 'Ждать более 8 ч, место: 1-5'


@pytest.mark.redis_store(
    ['set', 'AirportQueue:Zone:777:888', 'rostovondon_airport'],
)
@pytest.mark.config(
    AIRPORT_QUEUE_SETTINGS={'rostovondon_airport': {'USE_NEW_MESSAGES': True}},
)
def test_queue_details(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'qwerty', '888')

    @mockserver.json_handler('/tracker/1.0/airport-queue-info')
    def mock_tracker(request):
        return {
            'status': 'in',
            'rejects_count': 1,
            'queues': [
                {
                    'enabled': True,
                    'queue_count': 10,
                    'position': 3,
                    'class_name': 'econom',
                },
                {
                    'enabled': False,
                    'queue_count': 14,
                    'position': 3,
                    'class_name': 'business',
                },
                {
                    'enabled': True,
                    'queue_count': 10,
                    'position': 3,
                    'class_name': 'comfortplus',
                },
                {
                    'enabled': True,
                    'queue_count': 14,
                    'position': 3,
                    'class_name': 'business2',
                },
            ],
        }

    response = taxi_driver_protocol.get(
        'driver/queue/details?db=777&session=qwerty'
        '&zone_id=rostovondon_airport',
        headers={'Accept-Language': 'ru-RU'},
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['description']
    queues = response_obj['queues']
    assert len(queues) == 3
    queue_econom = queues[0]
    assert queue_econom['title_template']
    assert queue_econom['text'] == 'Ждать 1 ч 19 мин, место: 1-5'
    assert queue_econom['class_code'] == 1
    assert queue_econom['state']
    assert queue_econom['state_text']
    queue_comfort = queues[1]
    assert queue_comfort['title_template']
    assert queue_comfort['text'] == 'Ждать 1 ч 20 мин, место: 1-5'
    assert queue_comfort['class_code'] == 2
    assert not queue_comfort['state']
    assert queue_comfort['state_text'] != queue_econom['state_text']


@pytest.mark.redis_store(
    ['set', 'AirportQueue:Zone:777:888', 'rostovondon_airport'],
)
@pytest.mark.config(
    AIRPORT_QUEUE_SETTINGS={
        'rostovondon_airport': {
            'USE_NEW_MESSAGES': True,
            'SHOW_BEST_PARKING_WAITING_TIME': True,
        },
    },
)
def test_queue_details_dispatch(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'qwerty', '888')

    @mockserver.json_handler('/tracker/1.0/airport-queue-info')
    def mock_tracker(request):
        return {
            'status': 'in',
            'rejects_count': 1,
            'queues': [
                {
                    'enabled': True,
                    'queue_count': 10,
                    'position': 3,
                    'class_name': 'econom',
                },
                {
                    'enabled': True,
                    'queue_count': 14,
                    'position': 3,
                    'class_name': 'business',
                    'virtual': True,
                    'dispatch_positions': [
                        {
                            'area': 'rostovondon_airport_terminal_a',
                            'position': 14,
                        },
                        {
                            'area': 'rostovondon_airport_terminal_b',
                            'position': 12,
                        },
                        {
                            'area': 'rostovondon_airport_terminal_c',
                            'position': 9,
                        },
                    ],
                },
                {
                    'enabled': True,
                    'queue_count': 10,
                    'position': 3,
                    'class_name': 'comfortplus',
                },
                {
                    'enabled': True,
                    'queue_count': 14,
                    'position': 3,
                    'class_name': 'business2',
                },
            ],
        }

    response = taxi_driver_protocol.get(
        'driver/queue/details?db=777&session=qwerty'
        '&zone_id=rostovondon_airport',
        headers={'Accept-Language': 'ru-RU'},
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['description']
    queues = response_obj['queues']
    assert len(queues) == 3
    queue_econom = queues[0]
    assert queue_econom['title_template']
    assert queue_econom['text'] == 'Ждать 1 ч 19 мин, место: 1-5'
    assert queue_econom['class_code'] == 1
    assert queue_econom['state']
    assert queue_econom['state_text']
    queue_comfort = queues[1]
    assert queue_comfort['title_template']
    assert queue_comfort['text'] == 'Ждать 42 мин, место: 1-5'
    assert queue_comfort['class_code'] == 2


@pytest.mark.redis_store(
    ['set', 'AirportQueue:Zone:777:888', 'rostovondon_airport'],
)
@pytest.mark.config(
    AIRPORT_QUEUE_SETTINGS={
        'rostovondon_airport': {
            'USE_NEW_MESSAGES': True,
            'SHOW_BEST_PARKING_WAITING_TIME': True,
            'SHOW_BEST_PARKING_PLACE': True,
        },
    },
)
def test_queue_details_dispatch_position(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'qwerty', '888')

    @mockserver.json_handler('/tracker/1.0/airport-queue-info')
    def mock_tracker(request):
        return {
            'status': 'in',
            'rejects_count': 1,
            'queues': [
                {
                    'enabled': True,
                    'queue_count': 10,
                    'position': 3,
                    'class_name': 'econom',
                },
                {
                    'enabled': True,
                    'queue_count': 14,
                    'position': 3,
                    'class_name': 'business',
                    'virtual': True,
                    'dispatch_positions': [
                        {
                            'area': 'rostovondon_airport_terminal_a',
                            'position': 14,
                        },
                        {
                            'area': 'rostovondon_airport_terminal_b',
                            'position': 12,
                        },
                        {
                            'area': 'rostovondon_airport_terminal_c',
                            'position': 9,
                        },
                    ],
                },
                {
                    'enabled': True,
                    'queue_count': 10,
                    'position': 3,
                    'class_name': 'comfortplus',
                },
                {
                    'enabled': True,
                    'queue_count': 14,
                    'position': 3,
                    'class_name': 'business2',
                },
            ],
        }

    response = taxi_driver_protocol.get(
        'driver/queue/details?db=777&session=qwerty'
        '&zone_id=rostovondon_airport',
        headers={'Accept-Language': 'ru-RU'},
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['description']
    queues = response_obj['queues']
    assert len(queues) == 3
    queue_econom = queues[0]
    assert queue_econom['title_template']
    assert queue_econom['text'] == 'Ждать 1 ч 19 мин, место: 1-5'
    assert queue_econom['class_code'] == 1
    assert queue_econom['state']
    assert queue_econom['state_text']
    queue_comfort = queues[1]
    assert queue_comfort['title_template']
    assert queue_comfort['text'] == 'Ждать 42 мин, место: 6-10'
    assert queue_comfort['class_code'] == 2


@pytest.mark.translations(
    taximeter_messages=TAXIMETER_MESSAGES, tariff=TARIFF_MESSAGES,
)
@pytest.mark.config(
    DRIVER_PROTOCOL_UPDATE_AIRPORT_QUEUES_CACHE=True,
    DISPATCH_AIRPORT_QUEUE_UPDATE_ENABLED=True,
    DISPATCH_AIRPORT_ZONES={
        'ekb': {
            'use_queue': True,
            'enabled': True,
            'main_area': 'ekb_airport',
            'notification_area': 'ekb_airport_notification',
            'waiting_area': 'ekb_airport_waiting',
            'update_interval_sec': 1,
            'old_mode_enabled': True,
            'tariff_home_zone': 'ekb',
            'whitelist_classes': [],
            'airport_title_key': 'ekb_airport_key',
        },
    },
)
def test_request_dispatch_airport_queue_details(
        taxi_driver_protocol, mockserver, driver_authorizer_service, load_json,
):
    driver_authorizer_service.set_session('dbid', 'qwerty', 'uuid1')

    @mockserver.json_handler('/dispatch_airport/v1/info/drivers')
    def mock_dispatch_airport(request):
        return load_json('dispatch_airport_response.json')

    response = taxi_driver_protocol.get(
        'driver/queue/details',
        params={
            'db': 'dbid',
            'session': 'qwerty',
            'zone_id': 'ekb_airport_waiting',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    response_obj = response.json()

    assert response_obj['queues'] == [
        {
            'text': 'Ждать 1 ч, место: 16-20',
            'class_code': 1,
            'category_name': 'Эконом',
            'category_key': 'econom',
        },
        {
            'text': 'Ждать 1 ч 5 мин, место: 21-25',
            'class_code': 4,
            'category_name': 'Комфорт',
            'category_key': 'business',
        },
        {
            'text': 'Ждать более 2 ч, место: 21-25',
            'class_code': 8,
            'category_name': 'Минивэн',
            'category_key': 'minivan',
        },
        {
            'text': 'Ждать 50 мин, место: 31-35',
            'class_code': 128,
            'category_name': 'Универсал',
            'category_key': 'universal',
        },
        {
            'text': 'Ждать менее 5 мин, место: 1-5',
            'class_code': 512,
            'category_name': 'Комфорт+',
            'category_key': 'comfortplus',
        },
        {
            'text': 'Место: 1-5',
            'class_code': 1024,
            'category_name': 'Экспресс',
            'category_key': 'express',
        },
    ]
