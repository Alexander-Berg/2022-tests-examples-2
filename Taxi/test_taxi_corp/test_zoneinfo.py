# pylint: disable=redefined-outer-name

import pytest

_DOOR_TO_DOOR_REQUIREMENT = {
    'name': 'door_to_door',
    'label': 'От двери до двери',
    'type': 'boolean',
}

_CHILDCHAIR_REQUIREMENT = {
    'name': 'childchair_moscow',
    'label': 'Детское кресло',
    'type': 'select',
    'multiselect': True,
    'max_weight': 3,
    'select': {
        'options': [
            {
                'name': 'infant',
                'label': '9-18 кг',
                'weight': 2,
                'max_count': 1,
                'value': 1,
                'title': 'Малыш до 4 лет',
            },
            {
                'name': 'chair',
                'label': '15-25 кг',
                'weight': 2,
                'max_count': 1,
                'value': 3,
                'title': 'Ребёнок 3–7 лет',
            },
            {
                'name': 'booster',
                'label': '22-36 кг',
                'weight': 2,
                'max_count': 1,
                'value': 7,
                'title': 'Бустер',
            },
        ],
        'type': 'number',
    },
}

_ZONEINFO = {
    'moscow': {
        'zone_name': 'moscow',
        'zone_name_translate': 'Москва',
        'country_code': 'RU',
        'currency_code': 'RUB',
        'max_route_points_count': 5,
        'timezone': 'Europe/Moscow',
        'timezone_offset': '+0300',
        'tariff_classes': [
            {
                'name': 'econom',
                'name_translate': 'Эконом',
                'max_route_points_count': 5,
                'has_extra_contact_phone': False,
                'supported_requirements': [
                    _DOOR_TO_DOOR_REQUIREMENT,
                    _CHILDCHAIR_REQUIREMENT,
                ],
            },
            {
                'name': 'business',
                'name_translate': 'Комфорт',
                'max_route_points_count': 5,
                'has_extra_contact_phone': False,
                'supported_requirements': [],
            },
            {
                'name': 'express',
                'name_translate': 'Доставка',
                'max_route_points_count': 10,
                'has_extra_contact_phone': True,
                'supported_requirements': [],
            },
        ],
        'default_tariff_class': 'econom',
    },
    'ekb': {
        'zone_name': 'ekb',
        'zone_name_translate': 'Екатеринбург',
        'country_code': 'RU',
        'currency_code': 'RUB',
        'max_route_points_count': 3,
        'timezone': 'Asia/Yekaterinburg',
        'timezone_offset': '+0500',
        'tariff_classes': [
            {
                'name': 'econom',
                'name_translate': 'Эконом',
                'max_route_points_count': 3,
                'has_extra_contact_phone': False,
                'supported_requirements': [
                    _DOOR_TO_DOOR_REQUIREMENT,
                    _CHILDCHAIR_REQUIREMENT,
                ],
            },
            {
                'name': 'express',
                'name_translate': 'Доставка',
                'max_route_points_count': 7,
                'has_extra_contact_phone': True,
                'supported_requirements': [],
            },
        ],
        'default_tariff_class': 'econom',
    },
}


@pytest.fixture
def nearestzone_mock(patch):
    from taxi_corp.clients import protocol

    zones = {(37.642464, 55.735519): 'moscow', (60.597465, 56.838011): 'ekb'}

    @patch('taxi_corp.clients.protocol.ProtocolClient.nearestzone')
    async def _nearestzone(point, client_id=None, log_extra=None):
        zone = zones.get(tuple(point))
        if not zone:
            raise protocol.NotFoundError
        return zone


@pytest.mark.parametrize(
    'passport_mock, params, expected',
    [
        pytest.param(
            'client1',
            {'lon': '37.642464', 'lat': '55.735519', 'service': 'taxi'},
            _ZONEINFO['moscow'],
            id='moscow by point',
        ),
        pytest.param(
            'client1',
            {'lon': '60.597465', 'lat': '56.838011', 'service': 'taxi'},
            _ZONEINFO['ekb'],
            id='ekb by point',
        ),
        pytest.param(
            'client1',
            {'zone': 'moscow', 'service': 'taxi'},
            _ZONEINFO['moscow'],
            id='moscow by name',
        ),
        pytest.param(
            'client1',
            {'zone': 'ekb', 'service': 'taxi'},
            _ZONEINFO['ekb'],
            id='ekb by name',
        ),
        pytest.param(
            'client1',
            {
                'zone': 'moscow',
                'lon': '37.642464',
                'lat': '55.735519',
                'service': 'taxi',
            },
            _ZONEINFO['moscow'],
            id='moscow by point and name',
        ),
        pytest.param(
            'client1',
            {
                'name': 'ekb',
                'lon': '60.597465',
                'lat': '56.838011',
                'service': 'taxi',
            },
            _ZONEINFO['ekb'],
            id='ekb by point and name',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.translations(
    tariff={
        'name.express': {'ru': 'Доставка'},
        'name.business': {'ru': 'Комфорт'},
        'name.econom': {'ru': 'Эконом'},
        'name.vip': {'ru': 'Бизнес'},
    },
    client_messages={
        'requirement.door_to_door': {'ru': 'От двери до двери'},
        'requirement.childchair_moscow': {'ru': 'Детское кресло'},
        'requirement.childchair_moscow.infant': {'ru': '9-18 кг'},
        'requirement.childchair_moscow.infant_title': {'ru': 'Малыш до 4 лет'},
        'requirement.childchair_moscow.chair': {'ru': '15-25 кг'},
        'requirement.childchair_moscow.chair_title': {'ru': 'Ребёнок 3–7 лет'},
        'requirement.childchair_moscow.booster': {'ru': '22-36 кг'},
        'requirement.childchair_moscow.booster_title': {'ru': 'Бустер'},
    },
    geoareas={'moscow': {'ru': 'Москва'}, 'ekb': {'ru': 'Екатеринбург'}},
)
@pytest.mark.config(
    CORP_CATEGORIES={
        '__default__': {
            'express': 'name.express',
            'business': 'name.business',
            'econom': 'name.econom',
            'vip': 'name.vip',
        },
    },
    CORP_ORDER_EXTRA_PHONE_REQUIRED={
        '__default__': {'required': False},
        'courier': {'required': True},
        'express': {'required': True},
    },
)
async def test_general_get(
        nearestzone_mock,
        taxi_corp_real_auth_client,
        params,
        expected,
        passport_mock,
):
    response = await taxi_corp_real_auth_client.get(
        '/1.0/zoneinfo', params=params,
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == expected


@pytest.mark.parametrize(
    'passport_mock, params, expected_order',
    [
        pytest.param(
            'client1',
            {'lon': '37.642464', 'lat': '55.735519', 'service': 'taxi'},
            ['econom', 'express', 'business'],
            marks=pytest.mark.config(
                CORP_DEFAULT_CATEGORIES={
                    'rus': ['vip', 'express', 'business', 'econom'],
                },
            ),
            id='ordered with one redundant category in the config',
        ),
        pytest.param(
            'client1',
            {'lon': '37.642464', 'lat': '55.735519', 'service': 'taxi'},
            ['econom', 'express', 'business'],
            marks=pytest.mark.config(
                CORP_DEFAULT_CATEGORIES={'rus': ['express', 'econom']},
            ),
            id='ordered with one redundant category in the available classes',
        ),
        pytest.param(
            'client1',
            {'lon': '37.642464', 'lat': '55.735519', 'service': 'taxi'},
            ['econom', 'business', 'express'],
            marks=pytest.mark.config(CORP_DEFAULT_CATEGORIES={}),
            id='config is empty',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(
    CORP_CATEGORIES={
        '__default__': {
            'express': 'name.express',
            'business': 'name.business',
            'econom': 'name.econom',
            'vip': 'name.vip',
        },
    },
)
async def test_categories_order(
        nearestzone_mock,
        taxi_corp_real_auth_client,
        params,
        expected_order,
        passport_mock,
        taxi_config,
):

    response = await taxi_corp_real_auth_client.get(
        '/1.0/zoneinfo', params=params,
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    resulting_order = [
        item['name'] for item in response_json['tariff_classes']
    ]
    assert resulting_order == expected_order


@pytest.mark.parametrize(
    ['passport_mock', 'params', 'expected', 'status_code'],
    [
        pytest.param(
            'client1',
            {'lon': 'a', 'lat': '52.5842125', 'service': 'taxi'},
            {
                'errors': [
                    {
                        'text': (
                            'lon should be float could not'
                            ' convert string to float: \'a\''
                        ),
                        'code': 'GENERAL',
                    },
                ],
                'message': 'Invalid input',
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'fields': [
                        {
                            'message': (
                                'lon should be float could not'
                                ' convert string to float: \'a\''
                            ),
                            'code': 'GENERAL',
                        },
                    ],
                },
            },
            400,
            id='bad coords types',
        ),
        pytest.param(
            'client1',
            {'service': 'taxi'},
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'fields': [
                        {
                            'code': 'GENERAL',
                            'message': 'zone or lon/lat fields are required.',
                        },
                    ],
                },
                'errors': [
                    {
                        'code': 'GENERAL',
                        'text': 'zone or lon/lat fields are required.',
                    },
                ],
                'message': 'Invalid input',
            },
            400,
            id='point not exists',
        ),
        pytest.param(
            'client1',
            {'lon': '1', 'lat': '1', 'service': 'taxi'},
            {
                'code': 'GENERAL',
                'errors': [{'code': 'GENERAL', 'text': 'Zone not found'}],
                'message': 'Zone not found',
            },
            404,
            id='zone not found',
        ),
        pytest.param(
            'client1',
            {
                'zone': 'ekb',
                'lon': '37.642464',
                'lat': '55.735519',
                'service': 'taxi',
            },
            {
                'code': 'GENERAL',
                'errors': [{'code': 'GENERAL', 'text': 'Zone not found'}],
                'message': 'Zone not found',
            },
            404,
            id='zone name does not equal to point',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_general_get_fail(
        nearestzone_mock,
        taxi_corp_auth_client,
        params,
        expected,
        status_code,
        passport_mock,
):
    response = await taxi_corp_auth_client.get('/1.0/zoneinfo', params=params)
    response_json = await response.json()
    assert response.status == status_code, response_json
    assert response_json == expected
