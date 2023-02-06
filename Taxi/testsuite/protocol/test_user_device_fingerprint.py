import copy

import pytest


TEST_USER_PHONE_ID = '5e3810c6105e0da7568782a1'


def _make_afs_device_info_experiment(user_phone_id):
    return _make_experiment_v3(
        'user_phone_id',
        user_phone_id,
        'afs_pass_user_client_device_info',
        'protocol/user_client_device_info',
    )


def _make_afs_signature_experiment(user_phone_id):
    return _make_experiment_v3(
        'user_phone_id',
        user_phone_id,
        'afs_pass_user_client_signature',
        'protocol/user_client_device_info',
    )


def _make_experiment_v3(
        user_phone_id_arg_name, user_phone_id, exp_name, consumer,
):
    return {
        'name': exp_name,
        'consumers': [consumer],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_type': 'string',
                        'arg_name': user_phone_id_arg_name,
                        'value': user_phone_id,
                    },
                },
                'value': {},
            },
        ],
    }


def _make_base_params(
        user_id='user_id1',
        user_phone_id=TEST_USER_PHONE_ID,
        signature='signature1',
        device_info='device_info1',
        appmetrica_device_id='appmetrica_device_id1',
        taxi_device_id='taxi_device_id1',
        yandex_uid='yandex_uid1',
):
    return {
        'user_id': user_id,
        'user_phone_id': user_phone_id,
        'signature': signature,
        'device_info': device_info,
        'appmetrica_device_id': appmetrica_device_id,
        'taxi_device_id': taxi_device_id,
        'yandex_uid': yandex_uid,
    }


def _params_to_response(input):
    i = {k: v for k, v in input.items() if k not in ['signature', 'device_id']}
    i['user_info'] = input['device_info']
    return i


TEST_USER_DEVICE_FINGERPRINT_BASE_INPUT = [
    _make_base_params(signature=signature, device_info=device_info)
    for signature in ['signature1', None]
    for device_info in ['device_info1', None]
]


@pytest.mark.parametrize('input', TEST_USER_DEVICE_FINGERPRINT_BASE_INPUT)
@pytest.mark.experiments3(
    **_make_afs_device_info_experiment(TEST_USER_PHONE_ID),
)
@pytest.mark.experiments3(**_make_afs_signature_experiment(TEST_USER_PHONE_ID))
# happy path
def test_user_device_fingerprint_base(
        taxi_protocol, mockserver, blackbox_service, input,
):
    _test_user_device_fingerprint_base(
        taxi_protocol, mockserver, blackbox_service, input,
    )


@pytest.mark.parametrize('input', TEST_USER_DEVICE_FINGERPRINT_BASE_INPUT)
@pytest.mark.experiments3(**_make_afs_signature_experiment(TEST_USER_PHONE_ID))
def test_user_device_fingerprint_skip_device_info(
        taxi_protocol, mockserver, blackbox_service, input,
):
    _test_user_device_fingerprint_base(
        taxi_protocol,
        mockserver,
        blackbox_service,
        input,
        device_info_expected=False,
    )


@pytest.mark.parametrize('input', TEST_USER_DEVICE_FINGERPRINT_BASE_INPUT)
@pytest.mark.experiments3(
    **_make_afs_device_info_experiment(TEST_USER_PHONE_ID),
)
def test_user_device_fingerprint_skip_signature(
        taxi_protocol, mockserver, blackbox_service, input,
):
    _test_user_device_fingerprint_base(
        taxi_protocol,
        mockserver,
        blackbox_service,
        input,
        signature_expected=False,
    )


def _test_user_device_fingerprint_base(
        taxi_protocol,
        mockserver,
        blackbox_service,
        input,
        signature_expected=True,
        device_info_expected=True,
):
    @mockserver.json_handler('/uantifraud/v2/user/device_info')
    def mock_afs_check_sign(request):
        resp = request.json

        input_copy = copy.deepcopy(input)

        if signature_expected:
            assert resp.get('signature') == input_copy['signature']
            if 'signature' in resp:
                resp.pop('signature')
        input_copy.pop('signature')

        if device_info_expected:
            assert resp.get('device_info') == input_copy['device_info']
            if 'device_info' in resp:
                resp.pop('device_info')
        input_copy.pop('device_info')

        assert resp == input_copy

        return {}

    headers = {}
    req = {}

    input_copy = copy.deepcopy(input)

    if input_copy['signature'] is not None:
        headers['User-Data'] = input_copy['signature']
    input_copy.pop('signature')

    if input_copy['device_info'] is not None:
        req['user_info'] = input['device_info']
    input_copy.pop('device_info')

    req.update(input_copy)

    response = taxi_protocol.post(
        '/3.0/userinfo', headers=headers, bearer='test_token', json=req,
    )

    assert response.status_code == 200

    mock_afs_check_sign.wait_call()


def _test_no_experiment(
        taxi_protocol, blackbox_service, testpoint, testpoint_name,
):
    @testpoint(testpoint_name)
    def no_some_exp(_):
        pass

    input = _make_base_params()

    response = taxi_protocol.post(
        '/3.0/userinfo',
        headers={'User-Data': input['signature']},
        bearer='test_token',
        json=_params_to_response(input),
    )

    no_some_exp.wait_call()

    assert response.status_code == 200
