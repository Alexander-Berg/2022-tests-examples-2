# pylint: disable=unused-variable
import pytest

TRACKING_URL = '/eats/v1/eats-orders-tracking/v1/tracking'
MOCK_DATETIME = '2020-10-28T18:20:00.00+00:00'
PHONE_ROVER_SUPPORT = '+78006001234'
PHONE_CALL_CENTER = '+78006005678'


@pytest.fixture(name='mock_eda_candidates_list_by_ids')
def _mock_eda_candidates_list_by_ids(mockserver):
    @mockserver.json_handler('/eda-candidates/list-by-ids')
    def _handler_eda_candidates_list_by_ids(request):
        assert len(request.json['ids']) == 1
        mock_response = {'candidates': [{'position': [20.22, 10.11]}]}
        return mockserver.make_response(json=mock_response, status=200)


@pytest.fixture(name='mock_eats_personal')
def _mock_eats_personal(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _handler_eats_personal(request):
        mock_response = {}
        mock_response['items'] = []
        request_items = request.json['items']
        for request_item in request_items:
            item = {'id': request_item['id'], 'value': str(request_item['id'])}
            mock_response['items'].append(item)
        return mockserver.make_response(json=mock_response, status=200)


@pytest.fixture(name='mock_eats_cargo_claims')
def _mock_eats_cargo_claims(mockserver):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/points-eta',
    )
    def _handler_cargo_claims_info(request):
        return mockserver.make_response(json={}, status=200)

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/performer-position',
    )
    def _handler_cargo_claims_performer_position(request):
        return mockserver.make_response(json={}, status=200)


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.config(
    EATS_ORDERS_TRACKING_CALL_CENTER_PHONE={
        'call_center_phone': PHONE_CALL_CENTER,
    },
    EATS_ORDERS_TRACKING_CALL_TO_COURIER_BUTTON_BUILDING_STRATEGIES={
        '__default__': {
            'has_masked_phone': 'show_not_masked',
            'has_not_masked_phone': 'show_not_masked',
            'has_no_phone': 'show_contact_us',
            'unrecognized_error': 'show_contact_us',
        },
        'RU': {
            'has_masked_phone': 'show_masked',
            'has_not_masked_phone': 'show_not_masked',
            'has_no_phone': 'show_contact_us',
            'unrecognized_error': 'show_contact_us',
        },
    },
)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_data_for_call_courier.sql'],
)
@pytest.mark.experiments3(
    filename='exp3_display_matching_for_call_courier.json',
)
async def test_call_courier_button_builder(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        load_json,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
        mock_eats_cargo_claims,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    orders = response.json()['payload']['trackedOrders']
    assert response.status_code == 200
    assert len(orders) == 4

    # Personal courier phone number.
    assert orders[0]['order']['orderNr'] == '000000-000001'
    assert orders[0]['actions'] == [
        {
            'type': 'call',
            'title': 'button_title_1',
            'payload': {
                'contact_type': 'courier',
                'phone': '000001,000001',
                'alert_title': 'alert_title_key',
            },
            'actions': None,
        },
    ]

    assert orders[1]['order']['orderNr'] == '000000-000002'
    assert orders[1]['actions'] == [
        {
            'type': 'call',
            'title': 'button_title_1',
            'payload': {
                'contact_type': 'courier',
                'phone': '124',
                'alert_title': 'alert_title_key',
            },
            'actions': None,
        },
    ]

    assert orders[2]['order']['orderNr'] == '000000-000003'
    assert orders[2]['actions'] == [
        {
            'type': 'call',
            'title': 'button_title_1',
            'payload': {
                'contact_type': 'courier',
                'phone': '125',
                'alert_title': 'alert_title_key',
            },
            'actions': None,
        },
    ]

    # Masked courier phone number.
    assert orders[3]['order']['orderNr'] == '000000-000004'
    assert orders[3]['actions'] == [
        {
            'type': 'contact_us',
            'title': 'buttons.default.contact_us',
            'payload': {'alert_title': 'alert_title_key'},
            'actions': None,
        },
    ]
