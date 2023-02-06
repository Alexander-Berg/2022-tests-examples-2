import pytest


async def test_cancel_order_not_found(taxi_tristero_b2b, mockserver):
    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/cancel-order',
    )
    def _mock_parcels(request):
        return mockserver.make_response(status=404)

    response = await taxi_tristero_b2b.post(
        '/tristero/v1/cancel-order',
        json={
            'order_id': '123e4567-e89b-12d3-a456-426614174000',
            'reason': 'cause i can',
            'ref-doc': 'ref-doc_1',
            'doc-date': '2020-03-24T00:00:00Z',
        },
    )
    assert response.status_code == 404


async def test_cancel_order_wrong_order_id(taxi_tristero_b2b, mockserver):
    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/cancel-order',
    )
    def _mock_parcels(request):
        assert False

    response = await taxi_tristero_b2b.post(
        '/tristero/v1/cancel-order',
        json={
            'order_id': 'i am not uuid4',
            'reason': 'cause i can',
            'ref-doc': 'ref-doc_1',
            'doc-date': '2020-03-24T00:00:00Z',
        },
    )
    assert response.status_code == 400


async def test_cancel_order_ok(taxi_tristero_b2b, mockserver):
    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/cancel-order',
    )
    def _mock_parcels(request):
        return mockserver.make_response(status=200)

    response = await taxi_tristero_b2b.post(
        '/tristero/v1/cancel-order',
        json={
            'order_id': '123e4567-e89b-12d3-a456-426614174000',
            'reason': 'cause i can',
            'ref-doc': 'ref-doc_1',
            'doc-date': '2020-03-24T00:00:00Z',
        },
    )
    assert response.status_code == 200


@pytest.mark.parametrize('error_status', [400, 409])
async def test_cancel_order_error(taxi_tristero_b2b, mockserver, error_status):
    """ tristero-b2b should proxy error code
    from tristero-parcels """

    error_msg = 'conflict error message'
    order_id = '123e4567-e89b-12d3-a456-426614174000'

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/cancel-order',
    )
    def _mock_parcels(request):
        return mockserver.make_response(
            json={'message': error_msg}, status=error_status,
        )

    response = await taxi_tristero_b2b.post(
        '/tristero/v1/cancel-order',
        json={
            'order_id': order_id,
            'reason': 'cause i can',
            'ref-doc': 'ref-doc_1',
            'doc-date': '2020-03-24T00:00:00Z',
        },
    )
    assert response.status_code == error_status
    if error_status == 409:
        assert response.json()['message'] == error_msg
        assert response.json()['order_id'] == order_id
