import pytest


@pytest.mark.now('2021-01-01T12:00:00+0300')
@pytest.mark.parametrize(
    ['sip_username', 'expected_code', 'expected_data'],
    (
        pytest.param(
            '1000000000',
            200,
            {
                'user': '1609491900:1000000000',
                'password': 'qx8raySifeZUkdIPoh7qP+2hfDzoYnGLbFJffwvklvM=',
                'ttl': 300,
            },
            id='default config',
        ),
        pytest.param(
            '1000000000',
            200,
            {
                'user': '1609491901:1000000000',
                'password': 'qK0vd4Gmlzv+2CnPjxF4OyjJivtd1/9rWA1vvv4a0M4=',
                'ttl': 301,
            },
            marks=pytest.mark.config(
                CALLCENTER_REG_EPHEMERAL_TTL={'ttl': 301},
            ),
            id='normal config',
        ),
    ),
)
async def test_auth_ephemeral(
        taxi_callcenter_reg, sip_username, expected_code, expected_data,
):
    response = await taxi_callcenter_reg.post(
        '/v1/agent/auth/ephemeral', {'sip_username': sip_username},
    )
    assert response.status_code == expected_code
    assert response.json() == expected_data
