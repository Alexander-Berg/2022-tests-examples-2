import pytest


PARK_ID = 'park1'
DRIVER_ID = 'driver1'

# Generated via `tvmknife unittest service -s 111 -d 111`
OWN_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgQIbxBv:KG7QLOxr3cyYMdbkYLECvnEk'
    'imeu0G9106TLzuVqx4fJa6CPAo2jaC0ExoXhlp8cvCHdOSQ5lJy5kOX3'
    'oGJhMlKi6Dd1P5B1lo2k6uItSVMKfS7F1M2nEzr39PWtPd3tyeqARXEO'
    'ol80Mi7ZXd4wnDTusEYMeOvw417MXnMqBEE'
)
# Generated via `tvmknife unittest service -s 222 -d 111`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUI3gEQbw:CbnhjVPpWaQ9vKYuJsISgtV'
    'PLG97DGeKVHAH1YV_0DcAGuABWvcYqJvdDfnMjpMSZpGvDQk98J4qEhP_'
    'FMKwPUECoHQ0D2jYJTSYW0fabwvNE6K4o9e0_O3sW6_EJoJwYzOlrI7CJ'
    'GgbP4l7zVzHdENLYDqtfyEcc0pqoKZkgvU'
)


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'contractor-profession', 'dst': 'driver-profiles'}],
    TVM_SERVICES={'driver-profiles': 111, 'contractor-profession': 222},
    DRIVER_PROFILES_ORDERS_PROVIDER_SERVICES=['contractor-profession'],
)
@pytest.mark.tvm2_ticket({111: OWN_SERVICE_TICKET, 222: MOCK_SERVICE_TICKET})
@pytest.mark.parametrize(
    ('orders_providers', 'expected_code', 'expected_orders_providers'),
    [
        pytest.param(
            ['lavka', 'cargo'],
            200,
            {
                'eda': False,
                'lavka': True,
                'taxi': False,
                'cargo': True,
                'retail': False,
            },
            id='2 providers',
        ),
        pytest.param(
            ['eda', 'taxi', 'retail'],
            200,
            {
                'eda': True,
                'lavka': False,
                'taxi': True,
                'cargo': False,
                'retail': True,
            },
            id='3 providers',
        ),
        pytest.param(
            ['eda', 'taxi', 'retail'],
            200,
            {'eda': True},
            marks=pytest.mark.config(
                CONTRACTOR_PROFESSIONS_ORDERS_PROVIDERS_LIST=['eda'],
            ),
            id='unexpected providers',
        ),
        pytest.param([], 400, None, id='0 providers'),
        pytest.param(
            ['lavka', 'cargo'],
            400,
            None,
            marks=pytest.mark.config(
                CONTRACTOR_PROFESSIONS_ORDERS_PROVIDERS_LIST=['eda'],
            ),
            id='not allowed providers',
        ),
        pytest.param(['lavka', 'cargo'], 404, None, id='not found'),
    ],
)
async def test_courier_orders_providers_v2(
        taxi_driver_profiles,
        mockserver,
        mongodb,
        orders_providers,
        expected_code,
        expected_orders_providers,
):
    def _get_contractor():
        return mongodb.dbdrivers.find_one(
            dict(park_id=PARK_ID, driver_id=DRIVER_ID), {'orders_provider'},
        )

    author = {
        'consumer': 'contractor-profession',
        'identity': {'type': 'job', 'job_name': 'market'},
    }
    request_body = {'author': author, 'orders_providers': orders_providers}
    params = {'park_id': PARK_ID, 'driver_profile_id': DRIVER_ID}
    headers = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}
    if expected_code == 404:
        params['driver_profile_id'] = 'some_non_existing_id'

    response = await taxi_driver_profiles.put(
        '/v2/profile/orders-provider',
        params=params,
        json=request_body,
        headers=headers,
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        contractor = _get_contractor()
        assert contractor['orders_provider'] == expected_orders_providers
