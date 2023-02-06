DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


async def test_document(
        taxi_cargo_orders, default_order_id, fetch_order, mockserver,
):
    @mockserver.handler('/cargo-claims/v1/segments/get-document')
    def _claims(request):
        assert request.json == {
            'document_type': 'act',
            'point_id': 1,
            'driver': {
                'park_id': 'park_id1',
                'driver_profile_id': 'driver_id1',
            },
        }
        return mockserver.make_response(b'PDF FILE MOCK', 200)

    cargo_ref_id = 'order/' + default_order_id
    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/get-document',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': cargo_ref_id,
            'document_type': 'act',
            'point_id': 1,
        },
    )
    assert response.status_code == 200
    assert response.content == b'PDF FILE MOCK'
