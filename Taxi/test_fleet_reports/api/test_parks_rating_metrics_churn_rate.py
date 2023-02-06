import aiohttp.web
import pytest

from taxi.clients import personal

ENDPOINT = '/reports-api/v1/parks-rating/metrics/churn-rate'

DISTANCE = 5

RESPONSE = {
    'items': [
        {
            'id': 'a57d409d08a044fc9faab63aca103315',
            'last_order_date': '2021-02-01T03:22:39+03:00',
        },
        {
            'id': '284eff9f3524629d5b0eb5a833b7c772',
            'last_order_date': '2021-02-02T11:32:01+03:00',
            'full_name': 'Водитель Основной Про',
            'phone': '+70003402404',
            'work_rule_id': '656cbf2ed4e7406fa78ec2107ec9fefe',
            'work_status': 'working',
            'balance': 100.0,
            'license': '4521236547',
            'hire_date': '2020-03-19T03:00:00+03:00',
        },
        {
            'id': 'fdbb9ae4cec0458b813574f23e65c471',
            'last_order_date': '2021-02-06T01:03:50+03:00',
            'full_name': 'Тестовый Водитель2',
            'phone': '+70004356703',
            'work_rule_id': 'ddfc01154850483786fa7a5c8b90a184',
            'work_status': 'working',
            'balance': -373500.0,
            'license': '3407851764',
            'hire_date': '2018-02-07T16:17:30.589000+03:00',
        },
    ],
    'pagination': {'total': 3, 'page': 1, 'limit': 25},
}

RESPONSE_PERSONAL_TYPE_PHONES = [
    {'id': '75f707f5cc8e466c81ac9c35f8425b72', 'phone': '+70003402404'},
    {'id': 'd05cdbb2fe6941f8ad0a30ecd3d57aa8', 'phone': '+70004356703'},
]

RESPONSE_PERSONAL_TYPE_DRIVER_LICENSES = [
    {'id': '0f976569c4a44e07a6c4bf327a95036f', 'license': '4521236547'},
    {'id': '63460e0f5d8941ffba7a47124ee80221', 'license': '3407851764'},
]

FTA_QUERY = {
    'query': {
        'park': {
            'id': '7ad36bc7560449998acbe2c57a75c293',
            'driver_profile': {
                'ids': [
                    '284eff9f3524629d5b0eb5a833b7c772',
                    'fdbb9ae4cec0458b813574f23e65c471',
                ],
            },
        },
        'balance': {'accrued_ats': ['2021-05-04T12:48:44.477345+03:00']},
    },
}

FTA_RESPONSE = {
    'driver_profiles': [
        {
            'driver_profile_id': '284eff9f3524629d5b0eb5a833b7c772',
            'balances': [
                {
                    'accrued_at': '2021-05-04T12:33:11.882370+03:00',
                    'total_balance': '100.0000',
                },
            ],
        },
        {
            'driver_profile_id': 'fdbb9ae4cec0458b813574f23e65c471',
            'balances': [
                {
                    'accrued_at': '2021-05-04T12:33:11.882370+03:00',
                    'total_balance': '-373500.0000',
                },
            ],
        },
    ],
}


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
@pytest.mark.now('2021-05-04T12:48:44.477345+03:00')
async def test_success(
        web_app_client,
        headers,
        mock_driver_profiles,
        mock_fleet_transactions_api,
        patch,
        load_json,
):
    driver_profiles_stub = load_json('driver_profiles.json')

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _v1_driver_profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-reports'}
        assert request.json == driver_profiles_stub['request']
        return aiohttp.web.json_response(driver_profiles_stub['response'])

    @patch('taxi.clients.personal.PersonalApiClient.bulk_retrieve')
    async def _bulk_retrieve(data_type, request_ids, log_extra=None):
        if data_type == personal.PERSONAL_TYPE_PHONES:
            return RESPONSE_PERSONAL_TYPE_PHONES
        if data_type == personal.PERSONAL_TYPE_DRIVER_LICENSES:
            return RESPONSE_PERSONAL_TYPE_DRIVER_LICENSES

    @mock_fleet_transactions_api('/v1/parks/driver-profiles/balances/list')
    async def _v1_parks_driver_profiles_balances_list(request):
        assert request.json == FTA_QUERY
        return aiohttp.web.json_response(FTA_RESPONSE)

    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-03'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == RESPONSE


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
@pytest.mark.now('2021-05-04T12:48:44.477345+03:00')
async def test_empty(web_app_client, headers):
    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-04'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {
        'items': [],
        'pagination': {'limit': 25, 'page': 1, 'total': 0},
    }


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
@pytest.mark.now('2021-05-04T12:48:44.477345+03:00')
async def test_success_support_mode(
        web_app_client,
        headers_support,
        mock_driver_profiles,
        mock_fleet_transactions_api,
        patch,
        load_json,
):
    driver_profiles_stub = load_json('driver_profiles.json')

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _v1_driver_profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-reports'}
        assert request.json == driver_profiles_stub['request']
        return aiohttp.web.json_response(driver_profiles_stub['response'])

    @patch('taxi.clients.personal.PersonalApiClient.bulk_retrieve')
    async def _bulk_retrieve(data_type, request_ids, log_extra=None):
        if data_type == personal.PERSONAL_TYPE_PHONES:
            return RESPONSE_PERSONAL_TYPE_PHONES
        if data_type == personal.PERSONAL_TYPE_DRIVER_LICENSES:
            return RESPONSE_PERSONAL_TYPE_DRIVER_LICENSES

    @mock_fleet_transactions_api('/v1/parks/driver-profiles/balances/list')
    async def _v1_parks_driver_profiles_balances_list(request):
        assert request.json == FTA_QUERY
        return aiohttp.web.json_response(FTA_RESPONSE)

    items = []
    for item in RESPONSE['items']:
        if 'phone' in item:
            del item['phone']
        items.append(item)
    RESPONSE['items'] = items

    response = await web_app_client.get(
        ENDPOINT, headers=headers_support, params={'period': '2021-03'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == RESPONSE


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
@pytest.mark.now('2021-05-04T12:48:44.477345+03:00')
async def test_period_validator(web_app_client, headers):
    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-02'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {
        'items': [],
        'pagination': {'limit': 25, 'page': 1, 'total': 0},
    }
