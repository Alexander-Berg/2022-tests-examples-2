# pylint: disable=unused-variable
import pytest

TRACKING_URL = '/eats/v1/eats-orders-tracking/v1/tracking'


@pytest.fixture(name='mock_eda_candidates_list_by_ids')
def _mock_eda_candidates_list_by_ids(mockserver):
    @mockserver.json_handler('/eda-candidates/list-by-ids')
    def _handler_eda_candidates_list_by_ids(request):
        assert len(request.json['ids']) == 1
        mock_response = {'candidates': [{'position': [20.22, 10.11]}]}
        return mockserver.make_response(json=mock_response, status=200)


@pytest.mark.now('2020-10-28T18:20:00.00+00:00')
@pytest.mark.pgsql('eats_orders_tracking', files=['green_flow_payload.sql'])
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_green_flow(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        mock_eats_personal,
        mock_eda_candidates_list_by_ids,
):
    headers = make_tracking_headers(eater_id='eater1')
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=headers,
    )
    assert response.status_code == 200
    assert (
        response.json()['payload']['trackedOrders'][0]['title'] == 'car_title'
    )
    assert response.json()['payload']['trackedOrders'][0]['carInfo'] == {
        'car_brand': 'Kia Rio',
        'car_number': 'x000xx199',
        'car_plate': [
            {'type': 'letter', 'value': 'x'},
            {'type': 'number', 'value': '000'},
            {'type': 'letter', 'value': 'xx'},
            {'type': 'region', 'value': '199'},
        ],
        'description_template': '$DESCRIPTION$ $CAR_NUMBER$',
    }


@pytest.mark.now('2020-10-28T18:20:00.00+00:00')
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['invalid_car_number_payload.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_invalid_car_number(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        mock_eats_personal,
        mock_eda_candidates_list_by_ids,
):
    headers = make_tracking_headers(eater_id='eater1')
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=headers,
    )
    assert response.status_code == 200
    assert (
        response.json()['payload']['trackedOrders'][0]['title']
        == 'default_title'
    )
    assert response.json()['payload']['trackedOrders'][0]['carInfo'] is None
