import pytest

HEADERS = {'YaTaxi-Api-Key': 'secret'}


@pytest.mark.parametrize(
    'data,expected_code,expected_data',
    [
        ({'projection': [1]}, 400, None),
        ({'newer_than': 1}, 400, None),
        ({}, 200, None),
        (
            {'projection': ['_id']},
            200,
            {
                'countries': [
                    {'_id': 'rus'},
                    {'_id': 'aaa'},
                    {'_id': 'bbb'},
                    {'_id': 'ccc'},
                    {'_id': 'ddd'},
                ],
            },
        ),
        (
            {
                'projection': [
                    '_id',
                    'code2',
                    'phone_code',
                    'max_park_commission_for_subvention_percent',
                ],
            },
            200,
            {
                'countries': [
                    {
                        '_id': 'rus',
                        'code2': 'RU',
                        'phone_code': '7',
                        'max_park_commission_for_subvention_percent': 6,
                    },
                    {'_id': 'aaa', 'code2': 'AA'},
                    {'_id': 'bbb', 'code2': 'BB'},
                    {'_id': 'ccc', 'code2': 'CC'},
                    {'_id': 'ddd', 'code2': 'DD'},
                ],
            },
        ),
        (
            {'projection': ['_id'], 'newer_than': '2018-07-21T00:00:00.000Z'},
            200,
            {
                'countries': [
                    {'_id': 'aaa'},
                    {'_id': 'bbb'},
                    {'_id': 'ccc'},
                    {'_id': 'ddd'},
                ],
            },
        ),
        (
            {'projection': ['_id'], 'newer_than': '2018-07-23T00:00:00.000Z'},
            200,
            {'countries': [{'_id': 'aaa'}, {'_id': 'ddd'}]},
        ),
    ],
)
async def test_list(
        taxi_territories_client, data, expected_code, expected_data,
):
    response = await taxi_territories_client.post(
        '/v1/countries/list', headers=HEADERS, json=data,
    )
    assert response.status == expected_code
    content = await response.json()
    if expected_code != 200:
        assert 'status' in content
        assert 'details' in content
    if expected_data:
        assert content == expected_data


@pytest.mark.parametrize(
    'data,expected_code,expected_data',
    [
        ({'projection': ['test']}, 400, None),
        ({'_id': 'ussr'}, 404, None),
        (
            {'_id': 'rus', 'projection': ['currency', 'currency_rules']},
            200,
            {
                '_id': 'rus',
                'currency': 'RUB',
                'currency_rules': {
                    'fraction': 2,
                    'short_name': 'руб.',
                    'symbol': '₽',
                },
            },
        ),
        (
            {'_id': 'rus', 'projection': ['currency']},
            200,
            {'_id': 'rus', 'currency': 'RUB'},
        ),
        (
            {'_id': 'rus', 'projection': ['taximeter_supported_locales']},
            200,
            {'_id': 'rus', 'taximeter_supported_locales': ['test_locale']},
        ),
        (
            {'_id': 'rus', 'projection': ['taximeter_lang']},
            200,
            {'_id': 'rus', 'taximeter_lang': 'ru'},
        ),
    ],
)
async def test_retrieve(
        taxi_territories_client, data, expected_code, expected_data,
):
    response = await taxi_territories_client.post(
        '/v1/countries/retrieve', headers=HEADERS, json=data,
    )
    assert response.status == expected_code
    content = await response.json()
    if expected_code != 200:
        assert 'status' in content
        assert 'details' in content
    if expected_data:
        assert content == expected_data


@pytest.mark.parametrize(
    'country_id,name,data,expected_code',
    [
        (None, None, {'set': {'eng': 'Russia'}}, 400),
        ('test1', 'test2', {'set': {'eng': 'Russia'}}, 400),
        ('test1', None, {'set': {'eng': 'Russia'}}, 400),
        ('usr', None, {'set': {'eng': 'Russia'}}, 400),
        ('rus', None, {'set': {'eng': 'Russia'}, 'unset': ['eng']}, 400),
        ('rus', None, {'set': {'name': 'Россия'}}, 200),
        ('rus', None, {'set': {'eng': 'Russia'}}, 200),
        (
            'rus',
            None,
            {'set': {'eng': 'Russia'}, 'unset': ['state_service_url']},
            200,
        ),
        (
            'rus',
            None,
            {
                'set': {'eng': 'Russia', 'extra_field': None},
                'unset': ['state_service_url'],
            },
            400,
        ),
        (
            'rus',
            None,
            {
                'set': {'eng': 'Russia'},
                'unset': ['state_service_url', 'extra_field'],
            },
            400,
        ),
        ('rus', None, {'set': {'eng': 'Russia'}, 'unset': ['region_id']}, 400),
        (
            None,
            'Россия',
            {'set': {'taximeter_supported_locales': ['locale_TEST_2']}},
            200,
        ),
        (
            None,
            'Беларусь',
            {
                'set': {
                    'name': 'Беларусь',
                    'code2': 'BY',
                    'eng': 'Belarus',
                    'phone_code': '7',
                    'region_id': 225,
                    'phone_min_length': 11,
                    'phone_max_length': 11,
                    'national_access_code': '8',
                    'lang': 'ru',
                    'taximeter_supported_locales': ['test_locale'],
                    'state_service_url': 'test',
                },
            },
            400,
        ),
        (
            'bel',
            None,
            {
                'set': {
                    'name': 'Беларусь',
                    'code2': 'BY',
                    'eng': 'Belarus',
                    'region_id': 225,
                    'phone_min_length': 11,
                    'phone_max_length': 11,
                    'national_access_code': '8',
                    'lang': 'ru',
                    'taximeter_supported_locales': ['test_locale'],
                    'state_service_url': 'test',
                },
            },
            400,
        ),
        (
            'bel',
            None,
            {
                'set': {
                    'name': 'Беларусь',
                    'code2': 'BY',
                    'eng': 'Belarus',
                    'phone_code': '7',
                    'region_id': 225,
                    'phone_min_length': 11,
                    'phone_max_length': 11,
                    'national_access_code': '8',
                    'lang': 'ru',
                    'taximeter_supported_locales': ['test_locale'],
                    'state_service_url': 'test',
                },
            },
            200,
        ),
        (
            'bel',
            None,
            {
                'set': {
                    'name': 'Россия',
                    'code2': 'BY',
                    'eng': 'Belarus',
                    'phone_code': '7',
                    'region_id': 225,
                    'phone_min_length': 11,
                    'phone_max_length': 11,
                    'national_access_code': '8',
                    'lang': 'ru',
                    'taximeter_supported_locales': ['test_locale'],
                    'state_service_url': 'test',
                },
            },
            400,
        ),
        (
            'ccc',
            None,
            {
                'set': {
                    'eng': 'Cc',
                    'taximeter_supported_locales': ['test_locale'],
                },
            },
            200,
        ),
        (
            'ccc',
            None,
            {
                'set': {
                    'client_config': {
                        'phone_mask': '[000] [000]-[00]-[00]',
                        'phone_format': '900 000-00-00',
                    },
                    'tutorial_params': {
                        'web_experiment': 'test_web_experiment',
                        'show_in_settings': True,
                        'app_experiment': 'test_app_experiment',
                        'mode': 'app',
                        'web_tutorial_url': 'test_web_tutorial_url',
                        'fallback_to_web': False,
                    },
                },
            },
            200,
        ),
        (
            'bel',
            None,
            {
                'set': {
                    'name': 'Беларусь',
                    'code2': 'BY',
                    'eng': 'Belarus',
                    'phone_code': '7',
                    'region_id': 225,
                    'phone_min_length': 11,
                    'phone_max_length': 11,
                    'national_access_code': '8',
                    'lang': 'ru',
                    'taximeter_supported_locales': ['test_locale'],
                    'state_service_url': 'test',
                    'weekends': [
                        'monday',
                        'tuesday',
                        'wednesday',
                        'thursday',
                        'friday',
                        'saturday',
                        'sunday',
                    ],
                },
            },
            200,
        ),
        (
            'bel',
            None,
            {
                'set': {
                    'name': 'Беларусь',
                    'code2': 'BY',
                    'eng': 'Belarus',
                    'phone_code': '7',
                    'region_id': 225,
                    'phone_min_length': 11,
                    'phone_max_length': 11,
                    'national_access_code': '8',
                    'lang': 'ru',
                    'taximeter_supported_locales': ['test_locale'],
                    'state_service_url': 'test',
                    'weekends': [],
                },
            },
            200,
        ),
        (
            'bel',
            None,
            {
                'set': {
                    'name': 'Беларусь',
                    'code2': 'BY',
                    'eng': 'Belarus',
                    'phone_code': '7',
                    'region_id': 225,
                    'phone_min_length': 11,
                    'phone_max_length': 11,
                    'national_access_code': '8',
                    'lang': 'ru',
                    'taximeter_supported_locales': ['test_locale'],
                    'state_service_url': 'test',
                    'weekends': ['newday'],
                },
            },
            400,
        ),
    ],
)
async def test_update(
        taxi_territories_client, country_id, name, data, expected_code,
):
    async def _get_country():
        response = await taxi_territories_client.post(
            '/v1/countries/list', headers=HEADERS, json={},
        )
        countries = (await response.json())['countries']
        countries = [
            country
            for country in countries
            if country['_id'] == country_id or country['name'] == name
        ]
        return countries[0] if countries else None

    country_before = await _get_country()
    params = {}
    if country_id:
        params['id'] = country_id
    if name:
        params['name'] = name
    response = await taxi_territories_client.post(
        '/v1/countries/', headers=HEADERS, json=data, params=params,
    )
    assert response.status == expected_code
    content = await response.json()
    if expected_code != 200:
        assert 'status' in content
        assert 'details' in content
    else:
        country_after = await _get_country()
        data_set = data.get('set', {})
        for field in data_set:
            assert country_after[field] == data_set[field]
        data_unset = data.get('unset', [])
        for field in data_unset:
            assert field not in country_after
        if country_before:
            assert (
                country_before.keys() | data_set.keys()
                == country_after.keys() | set(data_unset)
            )


@pytest.mark.parametrize(
    'headers,auth_succeed',
    [(HEADERS, True), ({}, False), ({'X-Ya-Service-Ticket': '123'}, True)],
)
@pytest.mark.config(TVM_ENABLED=True)
async def test_tvm_auth(patch, taxi_territories_client, headers, auth_succeed):
    @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
    async def _get_allowed_service_name(ticket_body, log_extra=None):
        assert ticket_body is None or ticket_body == '123'
        return 'src-service-name'

    response = await taxi_territories_client.post(
        '/v1/countries/list', json={}, headers=headers,
    )
    if not auth_succeed:
        assert response.status == 403

    response = await taxi_territories_client.post(
        '/v1/countries/retrieve', json={}, headers=headers,
    )
    if not auth_succeed:
        assert response.status == 403

    response = await taxi_territories_client.post(
        '/v1/countries/', json={}, headers=headers,
    )
    if not auth_succeed:
        assert response.status == 403
