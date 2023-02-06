import pytest


@pytest.mark.parametrize('use_sintegro', ([True, False]))
async def test_v1_available_parkings(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        mockserver,
        use_sintegro,
):
    @mockserver.json_handler('/sintegro/ap/hs/available_parkings')
    def _available_parkings(request):
        return {'polygon_id': ['p1', 'p2']}

    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_PARTNER_PROTOCOL_USE_SINTEGRO_V2': {
                '__default__': use_sintegro,
            },
        },
    )
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    response = await taxi_dispatch_airport_partner_protocol.get(
        '/internal/v1/available_parkings',
    )
    assert response.status_code == 200
    if use_sintegro:
        assert response.json() == {'polygon_id': ['p1', 'p2']}
    else:
        assert response.json() == {'polygon_id': []}


@pytest.mark.config(
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_USE_SINTEGRO_V2={'__default__': True},
)
async def test_v1_available_parkings_negative(
        taxi_dispatch_airport_partner_protocol, mockserver,
):
    @mockserver.json_handler('/sintegro/ap/hs/available_parkings')
    def _available_parkings(request):
        return mockserver.make_response(status=500)

    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    response = await taxi_dispatch_airport_partner_protocol.get(
        '/internal/v1/available_parkings',
    )
    assert response.status_code == 500
