import operator

import pytest


@pytest.mark.parametrize(
    'passport_mock, lon, lat, service, expected',
    [
        (
            'client1',
            None,
            None,
            'taxi',
            [
                {'_id': 'business', 'name': 'Комфорт', 'tags': []},
                {'_id': 'start', 'name': 'Старт', 'tags': []},
                {'_id': 'econom', 'name': 'Эконом', 'tags': []},
            ],
        ),
        (
            'client1',
            '39.578377',
            None,
            'taxi',
            [
                {'_id': 'business', 'name': 'Комфорт', 'tags': []},
                {'_id': 'start', 'name': 'Старт', 'tags': []},
                {'_id': 'econom', 'name': 'Эконом', 'tags': []},
            ],
        ),
        (
            'client1',
            '39.578377',
            '52.5842125',
            'taxi',
            [
                {'_id': 'start', 'name': 'Старт', 'tags': []},
                {'_id': 'econom', 'name': 'Эконом', 'tags': []},
            ],
        ),
        (
            'client2',
            None,
            None,
            'taxi',
            [
                {'_id': 'cargo', 'name': 'Доставка', 'tags': ['cargo']},
                {'_id': 'start', 'name': 'Старт', 'tags': []},
                {'_id': 'econom', 'name': 'Эконом', 'tags': []},
            ],
        ),
        (
            'client3',
            None,
            None,
            'cargo',
            [
                {'_id': 'cargo', 'name': 'Доставка', 'tags': ['cargo']},
                {'_id': 'courier', 'name': 'Курьер', 'tags': ['cargo']},
            ],
        ),
        (
            'client4',
            None,
            None,
            'taxi',
            [
                {'_id': 'start', 'name': 'Старт', 'tags': []},
                {'_id': 'econom', 'name': 'Эконом', 'tags': []},
            ],
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.translations(
    tariff={
        'name.start': {'ru': 'Старт'},
        'name.business': {'ru': 'Комфорт'},
        'name.econom': {'ru': 'Эконом'},
        'name.vip': {'ru': 'Бизнес'},
        'name.cargo': {'ru': 'Доставка'},
        'name.courier': {'ru': 'Курьер'},
    },
)
@pytest.mark.config(
    CORP_CATEGORIES={
        '__default__': {
            'start': 'name.start',
            'business': 'name.business',
            'econom': 'name.econom',
            'vip': 'name.vip',
            'cargo': 'name.cargo',
        },
    },
    CORP_CARGO_CATEGORIES={
        '__default__': {'cargo': 'name.cargo', 'courier': 'name.courier'},
    },
    CORP_DEFAULT_CATEGORIES={'rus': ['start', 'econom', 'cargo']},
    CORP_WITHOUT_VAT_DEFAULT_CATEGORIES={'rus': ['start', 'econom']},
)
async def test_general_get(
        patch,
        taxi_corp_real_auth_client,
        lon,
        lat,
        service,
        expected,
        passport_mock,
):
    params = {'lon': lon, 'lat': lat, 'service': service}
    params = {key: value for key, value in params.items() if value}

    @patch('taxi_corp.clients.protocol.ProtocolClient.nearestzone')
    async def _nearestzone(point, client_id=None, log_extra=None):
        return 'lipetsk'

    response = await taxi_corp_real_auth_client.get(
        '/1.0/class', params=params,
    )
    response_json = (await response.json())['items']
    assert response.status == 200
    key = operator.itemgetter('_id')
    assert sorted(response_json, key=key) == sorted(expected, key=key)


@pytest.mark.parametrize(
    ['lon', 'lat', 'expected_result', 'status_code'],
    [
        (
            'a',
            '52.5842125',
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
        ),
    ],
)
async def test_general_get_fail(
        patch, taxi_corp_auth_client, lon, lat, expected_result, status_code,
):
    params = {'lon': lon, 'lat': lat}
    params = {key: value for key, value in params.items() if value}

    @patch('taxi_corp.clients.protocol.ProtocolClient.nearestzone')
    async def _nearestzone(point, client_id=None, log_extra=None):
        return 'lipetsk'

    response = await taxi_corp_auth_client.get('/1.0/class', params=params)
    assert response.status == status_code
    assert await response.json() == expected_result
