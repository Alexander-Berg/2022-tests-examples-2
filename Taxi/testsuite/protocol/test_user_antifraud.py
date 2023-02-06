import pytest


@pytest.mark.parametrize(
    'body, resp',
    [
        ({}, False),
        ({'ip': '123'}, False),
        ({'ip': '102.66.66.67'}, True),
        ({'position': {'lon': 37.000209, 'lat': 54.999363, 'dx': 100}}, True),
        ({'position': {'lon': 37.000167, 'lat': 54.998104, 'dx': 100}}, False),
        (
            {
                'ip': '102.66.66.67',
                'position': {'lon': 37.000167, 'lat': 54.998104, 'dx': 100},
            },
            True,
        ),
        (
            {
                'ip': '123',
                'position': {'lon': 37.000167, 'lat': 54.998104, 'dx': 100},
                'zone': 'moscow',
            },
            False,
        ),
        ({'application': 'android', 'application_version': '1.2.3'}, False),
        (
            {
                'application': 'android',
                'application_version': '1.2.3',
                'zone': 'moscow',
            },
            True,
        ),
        (
            {
                'application': 'android',
                'application_version': '2.3.4',
                'zone': 'moscow',
            },
            True,
        ),
        (
            {
                'application': 'android',
                'application_version': '2.3.5',
                'zone': 'moscow',
            },
            False,
        ),
        ({'application': 'iphone', 'application_version': '2.3.5'}, True),
        ({'application': 'iphone', 'application_version': '5.6.8'}, False),
        ({'zone': 'moscow', 'started_in_emulator': True}, True),
        ({'zone': 'moscow', 'started_in_emulator': False}, False),
        ({'started_in_emulator': True}, False),
        ({'zone': 'izhevsk', 'started_in_emulator': True}, False),
        ({'user_phone': '+79161234567', 'zone': 'moscow'}, True),
        ({'user_phone': '+79161234567', 'zone': 'spb'}, False),
        ({'user_phone': '+79171234567', 'zone': 'moscow'}, False),
        ({'user_phone': '+79031234567', 'zone': 'moscow'}, False),
        ({'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef'}, False),
        (
            {
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'zone': 'moscow',
            },
            True,
        ),
        (
            {
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cea',
                'zone': 'moscow',
            },
            False,
        ),
        (
            {
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
                'zone': 'spb',
            },
            False,
        ),
    ],
)
def test_user_antifraud(body, resp, taxi_protocol):
    response = taxi_protocol.post('utils/1.0/user-antifraud', json=body)
    assert response.status_code == 200
    assert response.json()['fraud'] == resp
