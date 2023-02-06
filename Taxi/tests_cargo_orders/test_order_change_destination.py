import pytest


@pytest.fixture(name='mock_claims_full')
def _mock_claims_full(mockserver, load_json):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def mock(request):
        return load_json('cargo-claims/default.json')

    return mock


@pytest.fixture(name='mock_intapi_change_destinations')
def _mock_intapi_change_destinations(mockserver):
    @mockserver.json_handler('/int-authproxy/v1/changedestinations')
    def changedestinations(request):
        return {
            'change_id': '3a78e3efbffb4700b8649c109e62b451',
            'name': 'name',
            'status': 'success',
            'value': [
                {
                    'type': 'address',
                    'country': 'Россия',
                    'fullname': 'Россия, Москва, 8 Марта, 4',
                    'geopoint': [33.1, 52.1],
                    'locality': 'Москва',
                    'porchnumber': '',
                    'premisenumber': '4',
                    'thoroughfare': '8 Марта',
                },
            ],
        }

    return changedestinations


async def test_basic(
        taxi_cargo_orders,
        mock_claims_full,
        default_order_id,
        mock_intapi_change_destinations,
):
    response = await taxi_cargo_orders.post(
        '/v1/order/change-destination',
        json={
            'order_id': default_order_id,
            'dispatch_version': 1,
            'claim_id': 'claim_seg1',
            'segment_id': 'seg1',
            'claim_point_id': 1,
            'idempotency_token': 'TOKEN-1',
        },
    )

    assert response.status_code == 200
    assert response.json() == {}

    assert mock_claims_full.times_called == 1
    assert mock_intapi_change_destinations.times_called == 1
    assert (
        mock_intapi_change_destinations.next_call()['request'].json[
            'idempotency_token'
        ]
        == 'TOKEN-1'
    )


async def test_not_found(taxi_cargo_orders, default_order_id):
    response = await taxi_cargo_orders.post(
        '/v1/order/change-destination',
        json={
            'order_id': '8971a845-36de-4b04-9662-626f9a0200c3',
            'dispatch_version': 1,
            'claim_id': 'claim_seg1',
            'segment_id': 'seg1',
            'claim_point_id': 1,
        },
    )

    assert response.status_code == 404


async def test_bad_input(
        taxi_cargo_orders,
        mock_claims_full,
        default_order_id,
        mock_intapi_change_destinations,
):
    response = await taxi_cargo_orders.post(
        '/v1/order/change-destination',
        json={
            'order_id': default_order_id,
            'dispatch_version': 1,
            'claim_id': 'claim_seg1',
            'segment_id': 'seg1',
            'claim_point_id': 666,
        },
    )

    assert response.status_code == 400
