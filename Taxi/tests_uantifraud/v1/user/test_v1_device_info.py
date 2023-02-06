import json

import pytest


@pytest.mark.parametrize(
    'user_id,user_phone_id,device_info_file,signature',
    [
        (
            'f9fa51b6d8864db3a5f9cf0d1fae910a',
            '5d833d55720026fa782037ef',
            'device_info.txt',
            'ChD4+rz0q3o9Vnf/3jfT35ZHEhDoix++9+WKzvtpjqfRCgSaGhZydS55YW'
            '5kZXgudGF4aS5kZXZlbG9wIJywRCgDMJnC3YmKLjoMV1m2B+gLaEcJxfUu',
        ),
    ],
)
async def test_base(
        taxi_uantifraud,
        load,
        mockserver,
        testpoint,
        mongodb,
        user_id,
        user_phone_id,
        device_info_file,
        signature,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_mds_s3(request):
        assert request.method == 'PUT'
        assert request.path == f'/mds-s3/user/device_info/full/{user_phone_id}'
        assert request.get_data().decode() == load('mds_data.txt').rstrip()
        return mockserver.make_response('OK', 200)

    @testpoint('prepare_data_for_mds')
    def _prepare_data_for_mds(data):
        assert data == json.loads(load('prepare_data_for_mds.json'))
        return {}

    response = await taxi_uantifraud.post(
        'v1/user/device_info',
        {
            'user_id': user_id,
            'user_phone_id': user_phone_id,
            'device_info': load(device_info_file),
            'signature': signature,
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    record = mongodb.antifraud_user_device_info.find_one(
        {'_id': user_phone_id},
    )

    assert record['device_info']['id'] == '28babff6581b6b587e8932742b86a3f2'

    assert record['signature'] == {
        'emulator': 0,
        'fake_gps': 4,
        'gps_switch': 0,
        'hook': 0,
        'millis': 1583252726041,
        'net_switch': 0,
        'plain_switch': 0,
        'root': 0,
        'sig_version': 3,
        'version_code': 1120284,
    }
