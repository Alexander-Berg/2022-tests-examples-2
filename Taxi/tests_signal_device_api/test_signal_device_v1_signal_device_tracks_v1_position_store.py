import pytest

from tests_signal_device_api import common


ENDPOINT = 'signal-device/v1/signal-device-tracks/device/v1/position/store'


POSITIONS = 'loltest123'


DEVICE_PRIMARY_KEY = 1
DEVICE_ID = 'device_id_test'
SERIAL_NUMBER = '123'
PARAMS = {'device_id': DEVICE_ID}


@pytest.mark.parametrize(
    'send_egts, park_id, software_version, is_fbs_v2',
    [
        (False, None, None, False),
        pytest.param(
            False,
            None,
            '01.1.1-1',
            True,
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_POSITION_STORE_SW_SETTINGS={
                    'software_version': '1.0.0-2',
                },
            ),
        ),
        pytest.param(
            False,
            None,
            '01.0.001-1',
            False,
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_POSITION_STORE_SW_SETTINGS={
                    'software_version': '1.0.0-2',
                },
            ),
        ),
        pytest.param(
            False,
            'p1',
            '1.1.1-1',
            False,
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_EGTS_INCLUDED_PARKS={'park_ids': []},
            ),
        ),
        pytest.param(
            True,
            'p1',
            None,
            False,
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_EGTS_INCLUDED_PARKS={'park_ids': ['p1']},
            ),
        ),
    ],
)
async def test_position_store(
        taxi_signal_device_api,
        pgsql,
        mockserver,
        send_egts,
        park_id,
        software_version,
        is_fbs_v2,
):
    @mockserver.json_handler(f'/signal-device-tracks/{ENDPOINT}')
    def _positions_store(request):
        assert request.json == POSITIONS
        if park_id is None:
            assert request.query['park_id'] == 'nopark'
        else:
            assert request.query['park_id'] == park_id
        assert request.query['serial_number'] == SERIAL_NUMBER
        assert request.query['send_egts'] == 'true' if send_egts else 'false'
        assert (
            request.query['fbs_schema_version'] == 'v2' if is_fbs_v2 else 'v1'
        )
        return {}

    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID, True, SERIAL_NUMBER,
    )

    if park_id is not None:
        db = pgsql['signal_device_api_meta_db'].cursor()
        query_str = f"""
            INSERT INTO signal_device_api.park_device_profiles
            (
                park_id,
                device_id,
                created_at,
                updated_at,
                is_active
            )
            VALUES
            (
                '{park_id}',
                (SELECT id FROM signal_device_api.devices
                 WHERE public_id = '{DEVICE_ID}'),
                NOW(),
                NOW(),
                TRUE
            )
        """
        db.execute(query_str)

    request_json = POSITIONS
    params = PARAMS
    if software_version is not None:
        params['software_version'] = software_version
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        json=request_json,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, PARAMS, request_json,
            ),
            'Content-Type': 'application/flatbuffer',
        },
        params=params,
    )
    assert response.status_code == 200, response.text
    assert _positions_store.times_called == 1
