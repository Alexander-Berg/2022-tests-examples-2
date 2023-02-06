import json

import pytest


@pytest.fixture
def mock_personal_driver_licenses_find(mockserver):
    @mockserver.json_handler('/personal/v1/driver_licenses/find')
    def mock_personal_driver_licenses_find(request):
        request_json = json.loads(request.get_data())
        driver_license_map = {
            'SUPERFRAUDER': '9725109e6e204ce28f67e6e91aaea099',
        }
        driver_license = request_json['value']
        if driver_license in driver_license_map:
            return {
                'id': driver_license_map[driver_license],
                'value': driver_license,
            }

        return mockserver.make_response({}, 404)


@pytest.fixture
def mock_personal_driver_licenses_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def mock_personal_retrieve(request):
        items = json.loads(request.get_data())['items']
        response_items = [
            {'id': i['id'], 'value': i['id'][:-6]}
            for i in items
            if i['id'].endswith('_pd_id')
        ]
        return {'items': response_items}


@pytest.mark.parametrize(
    'request_data, response_data',
    [
        (
            {
                'items': [
                    {
                        'type': 'driver_fix',
                        'billing_id': '100',
                        'data': {
                            'driver': {
                                'udi': 'udi1',
                                'license_personal_ids': ['lic1_pd_id'],
                            },
                            'period_end': '2019-01-10T09:00:00+1000',
                            'time_zone': 'Asia/Vladivostok',
                            'payment': '10',
                            'guarantee': '20',
                            'currency': 'USD',
                        },
                    },
                    {
                        'type': 'driver_fix',
                        'billing_id': '101',
                        'data': {
                            'driver': {
                                'udi': 'udi2',
                                'license_personal_ids': ['lic2_pd_id'],
                            },
                            'period_end': '2019-01-10T00:00:00+1000',
                            'time_zone': 'Europe/Moscow',
                            'payment': '500.500',
                            'guarantee': '100.100',
                            'currency': 'RUB',
                            'subvention': {
                                'amount': '837.3953',
                                'currency': 'RUB',
                            },
                        },
                    },
                ],
            },
            [
                {'action': 'pay', 'billing_id': '100'},
                {
                    'action': 'block',
                    'billing_id': '101',
                    'reason': {'id': 'test_rule1'},
                },
            ],
        ),
        (
            {
                'items': [
                    {
                        'type': 'driver_fix',
                        'billing_id': '102384563874',
                        'data': {
                            'driver': {
                                'udi': 'some_uid',
                                'license_personal_ids': ['SUPERFRAUDER_pd_id'],
                            },
                            'period_end': '2019-01-10T00:00:00+1000',
                            'time_zone': 'Europe/Moscow',
                            'payment': '212.55',
                            'guarantee': '12.00',
                            'currency': 'RUB',
                        },
                    },
                ],
            },
            [
                {
                    'action': 'block',
                    'billing_id': '102384563874',
                    'reason': {'id': 'test_rule2'},
                },
            ],
        ),
    ],
)
@pytest.mark.config(
    AFS_SUBVENTION_RULES_FETCH_LICENSE_PERSONAL_ID_FROM_PERSONAL=True,
)
def test_driver_fix_base(
        taxi_antifraud,
        mock_personal_driver_licenses_find,
        mock_personal_driver_licenses_retrieve,
        request_data,
        response_data,
):
    response = taxi_antifraud.post('v1/subventions/check', json=request_data)
    assert response.status_code == 200
    response = [
        {k: v for k, v in e.items() if k != 'antifraud_id'}
        for e in response.json()['items']
    ]
    assert response == response_data
