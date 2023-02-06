import pytest


_REQUEST = {
    'is_multiorder': False,
    'user_phone_id': 'user_phone_id1',
    'order_id': 'order_id1',
    'user_source_id': 'user_source_id1',
    'device_id': 'device_id1',
    'user_id': 'user_id1',
}


async def _test_base(taxi_uantifraud, request):
    resp = await taxi_uantifraud.post('/v1/user/is_blocked', json=request)
    assert resp.status_code == 200
    assert resp.json() == {'is_blocked': False}


async def test_base(taxi_uantifraud):
    await _test_base(taxi_uantifraud, _REQUEST)
    await _test_base(
        taxi_uantifraud,
        {'is_multiorder': False, 'user_phone_id': '618bc53e658288d92539861d'},
    )


@pytest.mark.now('2021-01-01T10:00:00+00:00')
async def test_blocked_by_phone_id(taxi_uantifraud):
    resp = await taxi_uantifraud.post(
        '/v1/user/is_blocked',
        json={**_REQUEST, **{'user_phone_id': '5bcd7548030553e658298f6c'}},
    )
    assert resp.status_code == 200
    assert resp.json() == {
        'is_blocked': True,
        'until': '2021-01-10T10:11:12+00:00',
    }


@pytest.mark.parametrize(
    'user_id_wl,user_source_id_wl,expected_resp',
    [
        (
            None,
            None,
            {'is_blocked': True, 'until': '2021-01-10T10:11:12+00:00'},
        ),
        ([_REQUEST['user_phone_id']], None, {'is_blocked': False}),
        (None, [_REQUEST['user_source_id']], {'is_blocked': False}),
    ],
)
@pytest.mark.now('2021-01-01T10:00:00+00:00')
async def test_blocked_by_device_id(
        taxi_uantifraud,
        taxi_config,
        user_id_wl,
        user_source_id_wl,
        expected_resp,
):
    taxi_config.set_values(
        {
            'AFS_IS_SPAMMER_WHITE_LIST': (
                [] if user_id_wl is None else user_id_wl
            ),
            'AFS_USER_SOURCES_WHITE_LIST': (
                [] if user_source_id_wl is None else user_source_id_wl
            ),
        },
    )

    resp = await taxi_uantifraud.post(
        '/v1/user/is_blocked',
        json={**_REQUEST, **{'device_id': 'fraud_device_id'}},
    )
    assert resp.status_code == 200
    assert resp.json() == expected_resp
