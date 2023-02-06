import json

import pytest


ENDPOINT = (
    '/signal-device/v1/signal-device-message-api/device/v1/mqtt-registration'
)


@pytest.mark.parametrize(
    'get_certs, del_cert_error',
    [
        ({'certificates': []}, False),
        (
            {
                'certificates': [
                    {'fingerprint': 'xxx', 'certificateData': 'kkk'},
                ],
            },
            False,
        ),
        (
            {
                'certificates': [
                    {'fingerprint': 'xxx', 'certificateData': 'xxx'},
                ],
            },
            False,
        ),
        (
            {
                'certificates': [
                    {'fingerprint': 'xxx', 'certificateData': 'xxx'},
                ],
            },
            True,
        ),
    ],
)
async def test_registration(
        taxi_signal_device_message_api,
        pgsql,
        mockserver,
        get_certs,
        del_cert_error,
):
    @mockserver.json_handler('/iot-devices-api-cloud/iot-devices/v1/devices')
    def _register_device(request):
        request_json = json.loads(request.get_data())
        assert request_json == {
            'certificates': [{'certificateData': 'xxx'}],
            'name': '123',
            'registryId': 'xxx',
        }

        assert request.headers['Authorization'] == 'Bearer xzxzxz123'

        return {'response': {'id': 'zzz'}}

    @mockserver.json_handler(
        '/iot-devices-api-cloud/iot-devices/v1/devices/zzz/certificates',
    )
    def _add_or_get_certificate(request):
        assert request.headers['Authorization'] == 'Bearer xzxzxz123'

        if request.method == 'GET':
            return get_certs

        request_json = json.loads(request.get_data())
        assert request_json == {'certificateData': 'kkk'}

        return {}

    @mockserver.json_handler(
        '/iot-devices-api-cloud/iot-devices/v1/devices/zzz/certificates/xxx',
    )
    def _del_certifcate(request):
        if del_cert_error:
            return mockserver.make_response(json={}, status=409)
        return {}

    response = await taxi_signal_device_message_api.post(
        ENDPOINT, json={'serial_number': '123', 'public_key': 'xxx'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'client_id': 'zzz'}

    db = pgsql['signal_device_message_api'].cursor()
    query_str = (
        'SELECT '
        ' client_id '
        'FROM signal_device_message_api.mqtt_device_bindings '
        'WHERE registry_id=\'xxx\' AND serial_number=\'123\''
    )
    db.execute(query_str)
    assert list(db)[0][0] == 'zzz'

    # retry
    response = await taxi_signal_device_message_api.post(
        ENDPOINT, json={'serial_number': '123', 'public_key': 'xxx'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'client_id': 'zzz'}
    assert _register_device.times_called == 1

    # retry new public key
    response = await taxi_signal_device_message_api.post(
        ENDPOINT, json={'serial_number': '123', 'public_key': 'kkk'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'client_id': 'zzz'}
    assert _add_or_get_certificate.times_called == 2

    certs = get_certs['certificates']
    if certs and certs[0]['certificateData'] != 'kkk':
        assert _del_certifcate.times_called == 1

    query_str = (
        'SELECT '
        ' public_key '
        'FROM signal_device_message_api.mqtt_device_bindings '
        'WHERE registry_id=\'xxx\' AND serial_number=\'123\''
    )
    db.execute(query_str)
    assert list(db)[0][0] == 'kkk'
