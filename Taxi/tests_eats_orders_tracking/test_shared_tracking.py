# pylint: disable=unused-variable
import pytest

SHARED_TRACKING_URL = '/eats/v1/eats-orders-tracking/v1/shared-tracking'
MOCK_DATETIME = '2020-10-28T18:20:00.00+00:00'


@pytest.fixture(name='mock_eda_candidates_list_by_ids')
def _mock_eda_candidates_list_by_ids(mockserver):
    @mockserver.json_handler('/eda-candidates/list-by-ids')
    def _handler_eda_candidates_list_by_ids(request):
        assert len(request.json['ids']) == 1
        mock_response = {'candidates': [{'position': [20.22, 10.11]}]}
        return mockserver.make_response(json=mock_response, status=200)


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
@pytest.mark.config(
    EATS_ORDERS_TRACKING_CONTACT_CENTER_PHONES={'__default__': '88006001210'},
)
async def test_green_flow(
        taxi_eats_orders_tracking, load_json, mock_eda_candidates_list_by_ids,
):
    response = await taxi_eats_orders_tracking.get(
        path=SHARED_TRACKING_URL, params={'shared_id': 'some_shared_id'},
    )
    expected_response = load_json('expected_response.json')
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
@pytest.mark.config(
    EATS_ORDERS_TRACKING_CONTACT_CENTER_PHONES={'__default__': '88006001210'},
)
async def test_shared_id_not_found(
        taxi_eats_orders_tracking, mock_eda_candidates_list_by_ids,
):
    response = await taxi_eats_orders_tracking.get(
        path=SHARED_TRACKING_URL, params={'shared_id': 'not_existed_id'},
    )
    assert response.status_code == 400
    assert response.json() == {
        'error_title': 'Заказ не найден',
        'error_description': (
            'Возможно, прошло уже слишком много времени после доставки'
        ),
    }
