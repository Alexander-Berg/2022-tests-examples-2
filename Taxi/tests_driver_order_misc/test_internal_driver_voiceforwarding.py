import pytest

EXPECTED_RESPONSE = {
    'order_id': '383e1b2cfeb03093accea972389eb8f4',
    'park_id': 'db',
    'driver_profile_id': '70a6137b04b9739f3577b11e5a182b14',
    'type': 'main',
}


def _set_mock_responses(protocol, parks):
    protocol.set_voiceforwarding(
        """
         <?xml version='1.0'?>
         <Forwardings>
             <Forwarding>
                 <Orderid>383e1b2cfeb03093accea972389eb8f4</Orderid>
                 <Phone>+70003990011</Phone>
                 <Ext>9003</Ext>
                 <TtlSeconds>900</TtlSeconds>
             </Forwarding>
         </Forwardings>
    """,
    )
    parks.set_driver_profiles_list(
        {
            'driver_profiles': [
                {'driver_profile': {'id': '70a6137b04b9739f3577b11e5a182b14'}},
            ],
            'offset': 0,
            'parks': [
                {
                    'id': '7ad36bc7560449998acbe2c57a75c293',
                    'provider_config': {
                        'upup': {'apikey': None, 'clid': None},
                        'yandex': {
                            'apikey': 'ba4a40f6e11f46f6b20ee7fa6000565d',
                            'clid': '100500',
                        },
                    },
                },
            ],
            'total': 1,
        },
    )


@pytest.mark.redis_store(
    [
        'hmset',
        'Order:SetCar:Drivers:db',
        {
            '383e1b2cfeb03093accea972389eb8f4': (
                '70a6137b04b9739f3577b11e5a182b14'
            ),
        },
    ],
)
async def test_ok(taxi_driver_order_misc, protocol, parks):
    _set_mock_responses(protocol, parks)
    response = await taxi_driver_order_misc.post(
        '/internal/driver-order-misc/v1/voiceforwarding',
        json=EXPECTED_RESPONSE,
    )
    assert response.status_code == 200
    assert response.json() == {
        'ext': '9003',
        'order_id': '383e1b2cfeb03093accea972389eb8f4',
        'phone': '+70003990011',
        'ttl_seconds': 900,
    }


async def test_no_redis_order(taxi_driver_order_misc):
    response = await taxi_driver_order_misc.post(
        '/internal/driver-order-misc/v1/voiceforwarding',
        json=EXPECTED_RESPONSE,
    )
    assert response.status_code == 404


@pytest.mark.redis_store(
    [
        'hmset',
        'Order:SetCar:Drivers:db',
        {'383e1b2cfeb03093accea972389eb8f4': 'other_driver'},
    ],
)
async def test_driver_id_mismatch_forbidden(
        taxi_driver_order_misc, protocol, parks,
):
    _set_mock_responses(protocol, parks)

    response = await taxi_driver_order_misc.post(
        '/internal/driver-order-misc/v1/voiceforwarding',
        json=EXPECTED_RESPONSE,
    )
    assert response.status_code == 404
