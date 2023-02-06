import pytest


async def test_invalid_session(taxi_bank_userinfo, mockserver):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/get_antifraud_info',
        json={'session_uuid': '024e7db5-9bd6-4f45-a1cd-2a442e15ffff'},
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'session_uuid, antifraud_info',
    [
        ('024e7db5-9bd6-4f45-a1cd-2a442e15bdf0', {}),
        (
            '024e7db5-9bd6-4f45-a1cd-2a442e15bdf1',
            {'device_id': 'device_id', 'dict': {'key': 'value'}},
        ),
    ],
)
async def test_ok(
        taxi_bank_userinfo, mockserver, session_uuid, antifraud_info,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/get_antifraud_info',
        json={'session_uuid': session_uuid},
    )

    assert response.status_code == 200
    assert response.json() == {
        'antifraud_info': antifraud_info,
        'created_at': '2021-10-31T00:01:00.0+00:00',
        'updated_at': '2021-10-31T00:02:00.0+00:00',
    }
