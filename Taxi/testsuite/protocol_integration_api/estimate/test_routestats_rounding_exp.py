import pytest


USER = {
    'phone': '+79061112255',
    'personal_phone_id': 'p00000000000000000000005',
    'user_id': 'e4707fc6e79e4562b4f0af20a8e877a6',
}

BASE_REQUEST = {
    'user': USER,
    'requirements': {'nosmoking': True},
    'route': [[37.1946401739712, 55.478983901730004], [37.565210, 55.734434]],
    'selected_class': 'econom',
    'sourceid': 'turboapp',
    'all_classes': False,
    'chainid': 'chainid_1',
    'agent': {'agent_user_type': 'individual', 'agent_id': 'gepard'},
}


@pytest.fixture
def mock_external(mockserver, load_json):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return load_json('get_four.json')

    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def mock_pin_storage_create_pin(request):
        return {}

    @mockserver.json_handler('/driver-eta/eta')
    def mock_eta_drivers(request):
        return load_json('eta_response.json')


@pytest.mark.parametrize(
    'exp_on,expected_message,expected_time,expected_time_raw',
    [
        pytest.param(
            False,
            '14 min',
            '1 min',
            1,
            marks=pytest.mark.experiments3(
                filename='experiments3_routestats_rounding_off.json',
            ),
            id='exp_off',
        ),
        pytest.param(
            True,
            '13 min',
            '2 min',
            2,
            marks=pytest.mark.experiments3(
                filename='experiments3_routestats_rounding_on.json',
            ),
            id='exp_on',
        ),
    ],
)
@pytest.mark.now('2020-01-21T11:30:00+0300')
class TestRoutestatsRoundingExp:
    def test_routestats_rounding(
            self,
            taxi_integration,
            mock_external,
            mockserver,
            exp_on,
            expected_message,
            expected_time,
            expected_time_raw,
            pricing_data_preparer,
    ):
        pricing_data_preparer.set_fixed_price(enable=True)
        pricing_data_preparer.set_trip_information(100, 100)
        pricing_data_preparer.set_strikeout(100)
        pricing_data_preparer.set_meta('min_price', 99)

        request = BASE_REQUEST
        response = taxi_integration.post('v1/orders/estimate', json=request)
        assert response.status_code == 200

        resp = response.json()
        resp_message = resp['service_levels'][0]['estimated_waiting'][
            'message'
        ]
        assert resp_message == expected_message

        resp_time = resp['service_levels'][0]['time']
        assert resp_time == expected_time

        resp_time_raw = resp['service_levels'][0]['time_raw']
        assert resp_time_raw == expected_time_raw
