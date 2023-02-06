import pytest

LANG_HEADER = 'Accept-Language'
USER_AGENT = 'User-Agent'
USER_AGENT_USUAL = 'Taximeter 8.88 (1234)'
REQUEST_HEADERS = {
    'X-Real-IP': '127.0.0.1',
    LANG_HEADER: 'ru',
    USER_AGENT: USER_AGENT_USUAL,
}

PARAGRAPH_1 = 'Заказы в аэропорту распределяются с помощью электронной очереди'
BULLET_1 = 'Едьте в аэропорт с заказом'

PARAGRAPH_2 = 'Заезжайте в зону ожидания аэропорта'
PARAGRAPH_3 = 'Либо с заказом, либо с репозишном, либо по тегу'


@pytest.mark.redis_store(['set', 'AirportQueue:Zone:777:driver', 'moscow'])
@pytest.mark.config(
    AIRPORT_QUEUE_SETTINGS={
        'moscow': {
            'ENABLED': True,
            'HIGH_GRADE': 100,
            'ACTIVATION_AREA': 'moscow_activation',
            'SURROUNDING_AREA': 'moscow_surrounding',
            'HOME_ZONE': 'moscow',
        },
    },
)
def test_simple_zone(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'qwerty', 'driver')

    response = taxi_driver_protocol.post(
        'driver/queue/zone?db=777&session=qwerty&zone_id=moscow&md5_zone_id=',
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['areas']) == 1
    area = data['areas'][0]
    assert 'geometry' in area
    assert 'properties' in area
    assert area['properties']['type'] == 'destination'
    assert 'options' in area
    assert area['options']['line_color'] == '#169CDC'
    assert area['options']['fill_color'] == '#48169CDC'
    assert 'md5' in data


@pytest.mark.redis_store(['set', 'AirportQueue:Zone:777:driver', 'moscow'])
@pytest.mark.config(
    AIRPORT_QUEUE_SETTINGS={
        'moscow': {
            'ENABLED': True,
            'HIGH_GRADE': 100,
            'ACTIVATION_AREA': 'moscow_activation',
            'SURROUNDING_AREA': 'moscow_surrounding',
            'HOME_ZONE': 'moscow',
        },
    },
)
def test_zone_same_md5(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'qwerty', 'driver')

    response = taxi_driver_protocol.post(
        'driver/queue/zone',
        headers=REQUEST_HEADERS,
        params={
            'db': '777',
            'session': 'qwerty',
            'zone_id': 'moscow',
            'md5_zone_id': '',
        },
    )
    assert response.status_code == 200
    data = response.json()
    md5 = data['md5']
    # second same request
    response = taxi_driver_protocol.post(
        'driver/queue/zone',
        headers=REQUEST_HEADERS,
        params={
            'db': '777',
            'session': 'qwerty',
            'zone_id': 'moscow',
            'md5_zone_id': md5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert 'areas' not in data
    assert data['md5'] == md5


@pytest.mark.redis_store(['set', 'AirportQueue:Zone:777:driver', 'moscow'])
@pytest.mark.config(
    AIRPORT_QUEUE_SETTINGS={
        'rostovondon_airport': {
            'VIEW_ENABLED': True,
            'ACTIVATION_AREA': 'rostovondon_airport',
        },
        'moscow': {
            'VIEW_ENABLED': True,
            'ACTIVATION_AREA': 'moscow_activation',
        },
    },
)
@pytest.mark.config(
    AIRPORT_QUEUE_ENABLE_PARKING_RECOMMENDATION_NAVIGATION=True,
)
def test_simple_zone_tracker(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/1.0/airport-queue-info')
    def mock_tracker(request):
        return {
            'status': 'in',
            'queues': [
                {
                    'enabled': True,
                    'queue_count': 14,
                    'class_name': 'econom',
                    'position': 11,
                },
            ],
            'rejects_count': 1,
            'recommended_parking_id': 'rostovondon_airport',
        }

    response = taxi_driver_protocol.post(
        'driver/queue/zone?db=777&session=qwerty&zone_id=moscow&md5_zone_id=',
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    zones = data['areas']
    assert len(zones) == 2
    assert 'geometry' in zones[0]
    geometry = zones[0]['geometry']
    assert 'coordinates' in geometry
    assert 'type' in geometry
    assert geometry['type'] == 'MultiPolygon'
    coordinates = geometry['coordinates']
    assert coordinates[0][0][0][0]

    assert zones[0]['properties']['type'] == 'outer'
    assert zones[0]['options']['line_color'] == '#169CDC'
    assert zones[0]['options']['fill_color'] == ''
    assert 'geometry' in zones[1]
    assert zones[1]['properties']['type'] == 'destination'
    assert zones[1]['options']['line_color'] == '#169CDC'
    assert zones[1]['options']['fill_color'] == '#48169CDC'

    assert 'md5' in data
    assert data['zone_main_point'] == [39.80166273136753, 47.25777007750279]


@pytest.mark.redis_store(['set', 'AirportQueue:Zone:777:driver', 'moscow'])
@pytest.mark.config(
    AIRPORT_QUEUE_ENABLE_PARKING_RECOMMENDATION_NAVIGATION=True,
)
@pytest.mark.config(
    AIRPORT_QUEUE_SETTINGS={
        'moscow': {
            'ENABLED': True,
            'HIGH_GRADE': 100,
            'ACTIVATION_AREA': 'moscow_activation',
            'SURROUNDING_AREA': 'moscow_surrounding',
            'HOME_ZONE': 'moscow',
        },
    },
)
def test_simple_zone_main_point(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'qwerty', 'driver')

    response = taxi_driver_protocol.post(
        'driver/queue/zone?db=777&session=qwerty&zone_id=moscow&md5_zone_id=',
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert 'md5' in data
    assert data['zone_main_point'] == [37.194640173971202, 55.478983901730004]
    assert 'rules' not in data


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
    DISPATCH_AIRPORT_OLD_VERSION_RULES=[
        {
            'tanker_key': 'dispatch_airport.rules.paragraph.about_queue',
            'is_bullet': False,
        },
    ],
    DISPATCH_AIRPORT_NEW_VERSION_RULES=[
        {
            'tanker_key': 'dispatch_airport.rules.paragraph.about_queue',
            'is_bullet': False,
        },
        {
            'tanker_key': 'dispatch_airport.rules.bullet.airport_order',
            'is_bullet': True,
        },
    ],
    DISPATCH_AIRPORT_OLD_MODE_RULES={
        'ekb': [
            {
                'tanker_key': 'dispatch_airport.rules.paragraph.old_mode',
                'is_bullet': False,
            },
        ],
    },
    DISPATCH_AIRPORT_NEW_MODE_RULES={
        'ekb': [
            {
                'tanker_key': 'dispatch_airport.rules.paragraph.new_mode',
                'is_bullet': False,
            },
        ],
    },
)
@pytest.mark.geoareas(filename='geoareas_ekb.json')
def test_request_dispatch_airport_zone(
        taxi_driver_protocol,
        mockserver,
        driver_authorizer_service,
        load_json,
        config,
):
    driver_authorizer_service.set_session('dbid', 'qwerty', 'uuid1')

    @mockserver.json_handler('/dispatch_airport/v1/info/drivers')
    def mock_dispatch_airport(request):
        return load_json('dispatch_airport_response.json')

    # unknown case
    response = taxi_driver_protocol.post(
        'driver/queue/zone',
        params={
            'db': 'dbid',
            'session': 'qwerty',
            'zone_id': 'unknown',
            'md5_zone_id': '',
        },
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 404

    # positive case
    response = taxi_driver_protocol.post(
        'driver/queue/zone',
        params={
            'db': 'dbid',
            'session': 'qwerty',
            'zone_id': 'ekb_airport_waiting',
            'md5_zone_id': '',
        },
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['areas']) == 1
    area = data['areas'][0]
    assert 'geometry' in area
    assert 'properties' in area
    assert area['properties']['type'] == 'destination'
    assert 'options' in area
    assert area['options']['line_color'] == '#169CDC'
    assert area['options']['fill_color'] == '#48169CDC'
    assert 'md5' in data
    assert data['rules'] == [{'text': PARAGRAPH_1, 'is_bullet': False}]

    # same md5 request
    md5 = data['md5']
    response = taxi_driver_protocol.post(
        'driver/queue/zone',
        headers=REQUEST_HEADERS,
        params={
            'db': 'dbid',
            'session': 'qwerty',
            'zone_id': 'ekb_airport_waiting',
            'md5_zone_id': md5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert 'areas' not in data
    assert data['md5'] == md5

    config.set_values(dict(DISPATCH_AIRPORT_USE_RULES_BY_AIRPORT=True))
    taxi_driver_protocol.invalidate_caches()
    response = taxi_driver_protocol.post(
        'driver/queue/zone',
        params={
            'db': 'dbid',
            'session': 'qwerty',
            'zone_id': 'ekb_airport_waiting',
            'md5_zone_id': '',
        },
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert 'md5' in data
    assert data['rules'] == [{'text': PARAGRAPH_2, 'is_bullet': False}]


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
            'old_mode_enabled': False,
            'tariff_home_zone': 'ekb',
            'whitelist_classes': [],
            'airport_title_key': 'ekb_airport_key',
        },
    },
    DISPATCH_AIRPORT_OLD_VERSION_RULES=[
        {
            'tanker_key': 'dispatch_airport.rules.paragraph.about_queue',
            'is_bullet': False,
        },
    ],
    DISPATCH_AIRPORT_NEW_VERSION_RULES=[
        {
            'tanker_key': 'dispatch_airport.rules.paragraph.about_queue',
            'is_bullet': False,
        },
        {
            'tanker_key': 'dispatch_airport.rules.bullet.airport_order',
            'is_bullet': True,
        },
    ],
    DISPATCH_AIRPORT_OLD_MODE_RULES={
        'ekb': [
            {
                'tanker_key': 'dispatch_airport.rules.paragraph.old_mode',
                'is_bullet': False,
            },
        ],
    },
    DISPATCH_AIRPORT_NEW_MODE_RULES={
        'ekb': [
            {
                'tanker_key': 'dispatch_airport.rules.paragraph.new_mode',
                'is_bullet': False,
            },
        ],
    },
)
@pytest.mark.geoareas(filename='geoareas_ekb.json')
def test_request_dispatch_airport_zone_old_mode_disabled(
        taxi_driver_protocol,
        mockserver,
        driver_authorizer_service,
        load_json,
        config,
):
    driver_authorizer_service.set_session('dbid', 'qwerty', 'uuid1')

    @mockserver.json_handler('/dispatch_airport/v1/info/drivers')
    def mock_dispatch_airport(request):
        return load_json('dispatch_airport_response.json')

    # unknown case
    response = taxi_driver_protocol.post(
        'driver/queue/zone',
        params={
            'db': 'dbid',
            'session': 'qwerty',
            'zone_id': 'unknown',
            'md5_zone_id': '',
        },
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 404

    # positive case
    response = taxi_driver_protocol.post(
        'driver/queue/zone',
        params={
            'db': 'dbid',
            'session': 'qwerty',
            'zone_id': 'ekb_airport_waiting',
            'md5_zone_id': '',
        },
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['areas']) == 1
    area = data['areas'][0]
    assert 'geometry' in area
    assert 'properties' in area
    assert area['properties']['type'] == 'destination'
    assert 'options' in area
    assert area['options']['line_color'] == '#169CDC'
    assert area['options']['fill_color'] == '#48169CDC'
    assert 'md5' in data
    rules = data['rules']
    rules.sort(key=lambda x: x['text'])
    assert rules == [
        {'text': BULLET_1, 'is_bullet': True},
        {'text': PARAGRAPH_1, 'is_bullet': False},
    ]

    config.set_values({'DISPATCH_AIRPORT_USE_RULES_BY_AIRPORT': True})
    taxi_driver_protocol.invalidate_caches()
    response = taxi_driver_protocol.post(
        'driver/queue/zone',
        params={
            'db': 'dbid',
            'session': 'qwerty',
            'zone_id': 'ekb_airport_waiting',
            'md5_zone_id': '',
        },
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert 'md5' in data
    rules = data['rules']
    assert rules == [{'text': PARAGRAPH_3, 'is_bullet': False}]


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
            'old_mode_enabled': False,
            'tariff_home_zone': 'ekb',
            'whitelist_classes': [],
            'airport_title_key': 'ekb_airport_key',
        },
    },
    DISPATCH_AIRPORT_OLD_VERSION_RULES=[
        {
            'tanker_key': 'dispatch_airport.rules.paragraph.about_queue',
            'is_bullet': False,
        },
    ],
    DISPATCH_AIRPORT_NEW_VERSION_RULES=[
        {
            'tanker_key': 'dispatch_airport.rules.paragraph.about_queue',
            'is_bullet': False,
        },
        {
            'tanker_key': 'dispatch_airport.rules.bullet.airport_order',
            'is_bullet': True,
        },
    ],
)
@pytest.mark.geoareas(filename='geoareas_ekb.json')
def test_request_dispatch_airport_unavailabe_airport_zone(
        taxi_driver_protocol, mockserver, driver_authorizer_service, load_json,
):
    driver_authorizer_service.set_session('dbid', 'qwerty', 'uuid1')

    @mockserver.json_handler('/dispatch_airport/v1/info/drivers')
    def mock_dispatch_airport(request):
        response = load_json('dispatch_airport_response.json')
        response['driver_infos'][0]['state'] = 'off'
        return response

    response = taxi_driver_protocol.post(
        'driver/queue/zone',
        params={
            'db': 'dbid',
            'session': 'qwerty',
            'zone_id': 'ekb_airport_waiting',
            'md5_zone_id': '',
        },
        headers=REQUEST_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['areas']) == 1
    area = data['areas'][0]
    assert area['options']['line_color'] == '#FA3E2C'
    assert area['options']['fill_color'] == '#14FA3E2C'
