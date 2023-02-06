import pytest

ENDPOINT = '/v1/contractor-profiles'


DRIVERS_DATA = {
    'park_with_offer_driver1': {
        'profiles': [
            {
                'park_driver_profile_id': 'park_with_offer_driver1',
                'data': {
                    'uuid': 'driver1',
                    'full_name': {
                        'first_name': 'Нурсултан',
                        'middle_name': 'Васильевич',
                        'last_name': 'Гамлет',
                    },
                    'created_date': '2017-08-03T09:30:42.965Z',
                    'work_status': 'working',
                    'phone_pd_ids': [{'pd_id': '0001'}],
                    'email_pd_ids': [{'pd_id': '0001'}],
                    'car_id': 'car1',
                    'balance_limit': '1000.0000',
                    'park_id': 'park_with_offer',
                },
            },
        ],
    },
    'park_with_offer_driver2': {
        'profiles': [
            {
                'park_driver_profile_id': 'park_with_offer_driver2',
                'data': {
                    'uuid': 'driver2',
                    'full_name': {
                        'first_name': 'Нур',
                        'middle_name': 'Сул',
                        'last_name': 'Тан',
                    },
                    'created_date': '2017-08-03T09:30:42.965Z',
                    'work_status': 'working',
                    'phone_pd_ids': [{'pd_id': '0001'}],
                    'email_pd_ids': [{'pd_id': '0001'}],
                    'park_id': 'park_with_offer',
                },
            },
        ],
    },
    'incorrect_park_driver2': {
        'profiles': [{'park_driver_profile_id': 'incorrect_park_driver2'}],
    },
}


@pytest.fixture(name='mock_driver_retrieve')
def _mock_driver_retrieve(mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_retrieve(request):
        driver_id = request.json['id_in_set'][0]
        return DRIVERS_DATA[driver_id]


@pytest.fixture(name='mock_vehicles_retrieve')
def _mock_vehicles_retrieve(mockserver):
    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _vehicles_retrieve(request):
        return {
            'vehicles': [
                {
                    'park_id_car_id': 'park_with_offer_car1',
                    'data': {
                        'car_id': 'car1',
                        'park_id': 'park_with_offer',
                        'number': 'A111AA11',
                        'brand': 'Kia',
                        'model': 'Rio',
                        'year': '2007',
                        'color': 'Белый',
                        'status': 'Active',
                    },
                },
            ],
        }


@pytest.fixture(name='mock_phones_retrieve')
def _mock_phones_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _phones_retrieve(request):
        pd_id = request.json['items'][0]['id']
        return {
            '0001': {'items': [{'id': '0001', 'value': '+79999999999'}]},
            '0002': {'items': []},
        }[pd_id]


@pytest.fixture(name='mock_emails_retrieve')
def _mock_emails_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/emails/bulk_retrieve')
    def _emails_retrieve(request):
        pd_id = request.json['items'][0]['id']
        return {
            '0001': {'items': [{'id': '0001', 'value': 'biba@boba.com'}]},
            '0002': {'items': []},
        }[pd_id]


@pytest.fixture(name='mock_fta_balances_list')
def _mock_fta_balances_list(mockserver):
    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _fta_balances_list(request):
        return {
            'driver_profiles': [
                {
                    'driver_profile_id': '123',
                    'balances': [
                        {
                            'accrued_at': request.json['query']['balance'][
                                'accrued_ats'
                            ][0],
                            'total_balance': '1050.5000',
                        },
                    ],
                },
            ],
        }


@pytest.mark.parametrize(
    'test_name,status_code',
    [('ok_1', 200), ('ok_2', 200), ('not_found', 404), ('bad_request', 403)],
)
async def test_contractor_profiles_get(
        taxi_gas_stations_api,
        test_name,
        status_code,
        load_json,
        mock_driver_retrieve,
        mock_vehicles_retrieve,
        mock_fta_balances_list,
        mock_phones_retrieve,
        mock_emails_retrieve,
        gas_stations,
):
    params = load_json(f'params/{test_name}.json')
    expected_response = load_json(f'responses/{test_name}.json')
    response = await taxi_gas_stations_api.get(ENDPOINT, params=params)
    assert response.status_code == status_code
    assert response.json() == expected_response
