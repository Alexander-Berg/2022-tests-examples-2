import pytest


@pytest.mark.now('2021-07-08T12:23:15.000+0000')
async def test_base(taxi_uantifraud, load, testpoint):
    @testpoint('proc_info')
    def _proc_info_tp(data):
        assert data == {
            'key_exists': True,
            'parse_success': True,
            'sign_decode_success': True,
            'sign_exists': True,
            'sign_not_expired': True,
        }

    @testpoint('sign_info')
    def _sign_info_tp(data):
        assert data == {
            'app_id': 'ru.yandex.taxi',
            'app_version_code': 30121968,
            'proto_version_code': 4,
            'time_millis': 1625746988524,
        }

    @testpoint('decode_status')
    def _decode_status_tp(data):
        assert data == {'decode_status': 0}

    @testpoint('legacy_detects')
    def _legacy_detects_tp(data):
        assert data == {
            'emulator': 0,
            'fake_gps': 0,
            'gps_switch': 1,
            'hook': 0,
            'net_switch': 0,
            'plane_switch': 0,
            'proto_version': 3,
            'root': 0,
            'time_millis': 1625746988524,
            'version_code': 30121968,
        }

    @testpoint('vm_detects')
    def _vm_detects_tp(data):
        assert data == []

    @testpoint('aux_data')
    def _aux_data_tp(data):
        assert data == [{'type': 1, 'value': '5'}, {'type': 2, 'value': '0'}]

    @testpoint('vm_aux_data')
    def _vm_aux_data_tp(data):
        assert data == []

    response = await taxi_uantifraud.post(
        'v2/user/device_info',
        {
            'user_id': 'f1550a8410c245929e2b40455e958f32',
            'user_phone_id': '55a2690b056f5f6f8223bb83',
            'signature': load('signature.txt'),
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    assert await _proc_info_tp.wait_call()
    assert await _sign_info_tp.wait_call()
    assert await _decode_status_tp.wait_call()
    assert await _legacy_detects_tp.wait_call()
    assert await _vm_detects_tp.wait_call()
    assert await _aux_data_tp.wait_call()
    assert await _vm_aux_data_tp.wait_call()


@pytest.mark.config(UAFS_USER_DEVICE_INFO_LOGGER_ENABLED=True)
async def test_yt_logger(taxi_uantifraud, testpoint):
    test_input = {
        'appmetrica_device_id': 'appmetrica_device_id1',
        'taxi_device_id': 'taxi_device_id1',
        'user_id': 'user_id1',
        'user_phone_id': 'user_phone_id1',
        'yandex_uid': 'yandex_uid1',
    }

    @testpoint('yt_logger_log')
    def _yt_logger_log(data):
        assert test_input.items() <= data.items()

    response = await taxi_uantifraud.post('v2/user/device_info', test_input)

    assert response.status_code == 200
    assert response.json() == {}

    assert await _yt_logger_log.wait_call()
