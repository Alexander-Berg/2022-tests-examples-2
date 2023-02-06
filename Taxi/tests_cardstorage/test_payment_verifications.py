# pylint: disable=too-many-lines
import copy
import datetime
import json

import pytest

from tests_cardstorage import common
from tests_cardstorage import configs


_UID = '4003514353'

TRUST_START_VERIFY_RESPONSE = {
    'uid': _UID,
    'binding_id': configs.CARD_ID,
    'verification': {
        'id': 'verification_id',
        'method': 'verification_method',
        'status': 'success',
        'start_ts': '2018-02-07T22:33:09.582Z',
    },
}

PASSED_PROCESSING_NAME = 'otkrytie'


def get_headers(
        login_id=None,
        language=None,
        user_id=None,
        pass_flags=None,
        personal=None,
        bound_uids=None,
):
    headers = {
        'X-Yandex-Uid': _UID,
        'X-Remote-IP': '127.0.0.1',
        'Accept-Language': 'ru_RU',
        'X-Request-Application': 'app_name=android',
        'X-AppMetrica-DeviceId': 'device_id',
    }
    if login_id is not None:
        headers['X-Login-Id'] = login_id
    if language is not None:
        headers['X-Request-Language'] = language
    if user_id is not None:
        headers['X-YaTaxi-UserId'] = user_id
    if pass_flags is not None:
        headers['X-YaTaxi-Pass-Flags'] = pass_flags
    if personal is not None:
        headers['X-YaTaxi-User'] = personal
    if bound_uids is not None:
        headers['X-YaTaxi-Bound-Uids'] = bound_uids
    return headers


def check_stq_task_call(
        stq,
        user_id,
        verification_id,
        card_id,
        user_uid,
        verification_status,
        verification_method,
):
    assert stq.save_card_verification.times_called == 1
    stq_call = stq.save_card_verification.next_call()
    assert stq_call['queue'] == 'save_card_verification'
    kwargs = {
        arg_name: value
        for arg_name, value in stq_call['kwargs'].items()
        if arg_name not in ('log_extra', '3ds_url')
    }
    assert kwargs == {
        'user_id': user_id,
        'verification_id': verification_id,
        'card_id': card_id,
        'user_uid': user_uid,
        'verification_status': verification_status,
        'verification_method': verification_method,
    }


def mark_afs_method(use_uafs):
    return [
        pytest.mark.config(
            CARDSTORAGE_GET_VERIFICATION_METHOD_FROM_ANTIFRAUD=True,
            UAFS_CARD_STORAGE_CHANGE_VERIFY_TYPE_DEST=use_uafs,
        ),
    ]


@configs.BILLING_SERVICE_NAME
@pytest.mark.config(TVM_ENABLED=True)
@common.tvm_ticket
@pytest.mark.parametrize('tvm, code', [(False, 401), (True, 200)])
async def test_payment_verifications_access(
        tvm, code, taxi_cardstorage, mongodb,
):
    body = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff77',
        'verification_id': '5cbf6b957c4448ac8964f0fcf3dbff77',
        'force_cache_invalidate': False,
    }
    headers = {'X-Ya-Service-Ticket': common.MOCK_TICKET if tvm else ''}
    headers.update(get_headers())
    response = await taxi_cardstorage.post(
        'v1/payment_verifications', json=body, headers=headers,
    )
    assert response.status_code == code


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize(
    'binding_id, verification_id, verification_status, verification_method',
    [
        (
            '6cbf6b957c4448ac8964f0fcf3dbff77',
            '5cbf6b957c4448ac8964f0fcf3dbff77',
            'in_progress',
            'auto',
        ),
        (
            '6cbf6b957c4448ac8964f0fcf3dbff80',
            '5cbf6b957c4448ac8964f0fcf3dbff81',
            'cvn_expected',
            'standard2',
        ),
    ],
)
async def test_simple(
        taxi_cardstorage,
        mongodb,
        binding_id,
        verification_id,
        verification_status,
        verification_method,
):
    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(),
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': binding_id,
            'verification_id': verification_id,
            'force_cache_invalidate': False,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'binding_id': binding_id,
        'verification': {
            'id': verification_id,
            'method': verification_method,
            'status': verification_status,
        },
    }


@configs.BILLING_SERVICE_NAME
async def test_sort(taxi_cardstorage, mongodb):
    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(),
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff79',
            'force_cache_invalidate': False,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff79',
        'verification': {
            'id': '5cbf6b957c4448ac8964f0fcf3dbff79',
            'method': 'auto',
            'status': '3ds_required',
            'finish_binding_url': 'https://ya.ru',
            '3ds_url': 'https://ya.ru',
        },
    }


async def test_404(taxi_cardstorage, mongodb, mockserver):
    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(),
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'verification_id': '5cbf6b957c4448ac8964f0fcf3dbff78',
            'force_cache_invalidate': False,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        'error': {'text': 'Verification or binding not found'},
    }


# Enabling this config to ensure that it does not affect URLs used for
# verification
USE_TRUST_ATLAS = pytest.mark.config(
    CARDSTORAGE_USE_ATLAS_BINDINGS_PROBABILITY=1.0,
)


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize(
    'brand,token',
    [
        ('yango', 'taxifee_8c7078d6b3334e03c1b4005b02da30f4'),
        ('yauber', 'ubertaxi_4ea0f5fc283dc942c27bc7ae022e8821'),
        pytest.param(
            'yango',
            'taxifee_8c7078d6b3334e03c1b4005b02da30f4',
            marks=[USE_TRUST_ATLAS],
        ),
    ],
)
async def test_request_verification_update(
        taxi_cardstorage, mongodb, mockserver, brand, token, stq,
):
    card_id = '6cbf6b957c4448ac8964f0fcf3dbff78'
    verification_id = '5cbf6b957c4448ac8964f0fcf3dbff78'
    user_uid = _UID

    verification_method = 'auto'
    verification_status = '3ds_required'

    @mockserver.json_handler(
        f'/trust-lpm/bindings/6cbf6b957c4448ac8964f'
        '0fcf3dbff78/verifications/5cbf6b957c4448ac8964'
        'f0fcf3dbff78/',
    )
    def mock_trust(request):
        assert request.headers['X-Service-Token'] == token
        return {
            'uid': user_uid,
            'binding_id': card_id,
            'verification': {
                '3ds_url': (
                    'https://trust-test.yandex.ru/web/redirect_3ds?'
                    'purchase_token=5cbf6b957c4448ac8964f0fcf3dbff78'
                ),
                'id': verification_id,
                'method': verification_method,
                'status': verification_status,
                'start_ts': '2018-02-07T22:33:09.582Z',
            },
        }

    headers = get_headers()
    headers['X-Request-Application'] = 'app_brand=' + brand
    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=headers,
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': card_id,
            'verification_id': verification_id,
            'force_cache_invalidate': True,
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        'binding_id': card_id,
        'verification': {
            'id': verification_id,
            'method': verification_method,
            'status': verification_status,
            '3ds_url': (
                'https://trust-test.yandex.ru/web/redirect_3ds?'
                'purchase_token=5cbf6b957c4448ac8964f0fcf3dbff78'
            ),
        },
    }

    obj = mongodb.trust_verifications.find_one(
        {'binding_id': card_id}, {'_id': 0},
    )
    assert obj == {
        'uid': user_uid,
        'binding_id': card_id,
        'verification_id': verification_id,
        'method': verification_method,
        'status': verification_status,
        'start_ts': datetime.datetime(2018, 2, 7, 22, 33, 9, 582000),
        '3ds_url': (
            'https://trust-test.yandex.ru/web/redirect_3ds?'
            'purchase_token=5cbf6b957c4448ac8964f0fcf3dbff78'
        ),
    }
    assert mock_trust.times_called == 1

    check_stq_task_call(
        stq,
        '',
        verification_id,
        card_id,
        user_uid,
        verification_status,
        verification_method,
    )


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize(
    'card_id, login_id, verification_id, verification_status, '
    'verification_method',
    [
        (
            '6cbf6b957c4448ac8964f0fcf3dbff78',
            'some-login-id',
            '5cbf6b957c4448ac8964f0fcf3dbff78',
            'in_progress',
            'auto',
        ),
        (
            '6cbf6b957c4448ac8964f0fcf3dbff80',
            'some-login-id',
            '5cbf6b957c4448ac8964f0fcf3dbff81',
            'success',
            'standard2',
        ),
        (
            '6cbf6b957c4448ac8964f0fcf3dbff80',
            None,
            '5cbf6b957c4448ac8964f0fcf3dbff81',
            'success',
            'standard2',
        ),
    ],
)
async def test_request_binding_update(
        taxi_cardstorage,
        mongodb,
        mockserver,
        stq,
        card_id,
        login_id,
        verification_id,
        verification_status,
        verification_method,
):
    user_uid = _UID

    @mockserver.json_handler('/trust-lpm/bindings/{}/verify/'.format(card_id))
    def mock_trust(request):
        assert 'currency' not in request.json
        if login_id is not None:
            assert request.headers['X-Login-Id'] == login_id
        else:
            assert 'X-Login-Id' not in request.headers
        return {
            'uid': user_uid,
            'binding_id': card_id,
            'verification': {
                'id': verification_id,
                'method': verification_method,
                'status': verification_status,
                'start_ts': '2018-02-07T22:33:09.582Z',
            },
        }

    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(login_id=login_id),
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': card_id,
            'force_cache_invalidate': True,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'binding_id': card_id,
        'verification': {
            'id': verification_id,
            'method': verification_method,
            'status': verification_status,
        },
    }

    obj = mongodb.trust_verifications.find_one(
        {'binding_id': card_id}, {'_id': 0},
    )
    assert obj == {
        'uid': user_uid,
        'binding_id': card_id,
        'verification_id': verification_id,
        'method': verification_method,
        'status': verification_status,
        'start_ts': datetime.datetime(2018, 2, 7, 22, 33, 9, 582000),
    }
    assert mock_trust.times_called == 1

    check_stq_task_call(
        stq,
        '',
        verification_id,
        card_id,
        user_uid,
        verification_status,
        verification_method,
    )


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize('processing_name', [None, configs.PROCESSING_NAME])
async def test_processing_name(
        taxi_cardstorage, mockserver, processing_name, experiments3,
):
    if processing_name:
        experiments3.add_config(
            name='binding_processing_name',
            consumers=['cardstorage/payment_verifications'],
            default_value={'processing_name': processing_name},
        )

    @mockserver.json_handler(
        '/trust-lpm/bindings/{}/verify/'.format(configs.CARD_ID),
    )
    def mock_trust(request):
        pass_params = request.json['pass_params']
        if processing_name:
            terminal_route_data = pass_params['terminal_route_data']
            assert (
                terminal_route_data['preferred_processing_cc']
                == processing_name
            )
        else:
            assert 'terminal_route_data' not in pass_params.keys()

        return TRUST_START_VERIFY_RESPONSE

    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(login_id='login_id'),
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': configs.CARD_ID,
            'force_cache_invalidate': True,
        },
    )

    assert response.status_code == 200
    assert mock_trust.times_called == 1


@configs.BILLING_FORM_HOST
@configs.BILLING_SERVICE_NAME
async def test_change_3ds_host(taxi_cardstorage, mockserver):
    prev_host = 'trust.ru'
    trust_url = f'https://{prev_host}/process_3ds?id=123'
    changed_url = f'https://{configs.CHANGED_HOST}/process_3ds?id=123'

    @mockserver.json_handler(
        '/trust-lpm/bindings/{}/verify/'.format(configs.CARD_ID),
    )
    def mock_trust(request):
        response = copy.deepcopy(TRUST_START_VERIFY_RESPONSE)
        response['verification']['method'] = 'standard2_3ds'
        response['verification']['3ds_url'] = trust_url

        return response

    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(login_id='login_id'),
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': configs.CARD_ID,
            'force_cache_invalidate': True,
        },
    )

    assert response.status_code == 200
    assert response.json()['verification']['3ds_url'] == changed_url
    assert mock_trust.times_called == 1


@configs.BILLING_SERVICE_NAME
@configs.CARDSTORAGE_AVS_DATA
@pytest.mark.parametrize(
    'json_request, avs_data_expected',
    [
        (
            {
                'id': 'b300bda7d41b4bae8d58dfa93221ef16',
                'binding_id': configs.CARD_ID,
                'force_cache_invalidate': True,
            },
            {
                'avs_post_code': configs.AVS_POST_CODE,
                'avs_street_address': configs.AVS_STREET_ADDRESS,
            },
        ),
        (
            {
                'id': 'b300bda7d41b4bae8d58dfa93221ef16',
                'binding_id': configs.CARD_ID,
                'force_cache_invalidate': True,
                'pass_params': {
                    'avs_data': {
                        'post_code': configs.AVS_POST_CODE_PASSED,
                        'street_address': configs.AVS_STREET_ADDRESS_PASSED,
                    },
                },
            },
            {
                'avs_post_code': configs.AVS_POST_CODE_PASSED,
                'avs_street_address': configs.AVS_STREET_ADDRESS_PASSED,
            },
        ),
    ],
)
async def test_avs_data_in_pass_params(
        taxi_cardstorage, mockserver, json_request, avs_data_expected,
):
    @mockserver.json_handler(
        '/trust-lpm/bindings/{}/verify/'.format(configs.CARD_ID),
    )
    def mock_trust(request):
        pass_params = request.json['pass_params']
        avs_data = pass_params['avs_data']
        assert avs_data == avs_data_expected

        return TRUST_START_VERIFY_RESPONSE

    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(login_id='login_id'),
        json=json_request,
    )

    assert response.status_code == 200
    assert mock_trust.times_called == 1


@configs.BINDING_RETURN_PATH_URL
@configs.BILLING_SERVICE_NAME
async def test_return_path(taxi_cardstorage, mockserver):
    @mockserver.json_handler(
        '/trust-lpm/bindings/{}/verify/'.format(configs.CARD_ID),
    )
    def mock_trust(request):
        return_path = request.json['return_path']
        assert return_path == configs.RETURN_PATH

        return TRUST_START_VERIFY_RESPONSE

    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(login_id='login_id'),
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': configs.CARD_ID,
            'force_cache_invalidate': True,
        },
    )

    assert response.status_code == 200
    assert mock_trust.times_called == 1


@configs.BILLING_SERVICE_NAME
@pytest.mark.config(
    CARD_BINDING_TRUST_ERROR_CODE_TO_TRANSLATION_ERROR_CODE_MAP={
        '__default__': 'card_binding_error_message.default',
        'declined_by_issuer': 'card_binding_error_message.refer_your_bank',
    },
)
@pytest.mark.translations(
    client_messages={
        'card_binding_error_message.default': {'ru': 'Ошибка по-умолчанию'},
        'card_binding_error_message.refer_your_bank': {
            'ru': 'Обратитесь в ваш банк',
        },
    },
)
@pytest.mark.parametrize(
    'authorize_rc, error_message',
    [
        (None, 'Ошибка по-умолчанию'),
        ('declined_by_issuer', 'Обратитесь в ваш банк'),
    ],
)
async def test_request_error_message(
        taxi_cardstorage, mockserver, authorize_rc, error_message,
):
    @mockserver.json_handler(
        '/trust-lpm/bindings/6cbf6b957c4448ac8964f0fcf3dbff78/verify/',
    )
    def mock_trust(request):
        assert 'currency' not in request.json
        response = {
            'uid': _UID,
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'verification': {
                'id': '5cbf6b957c4448ac8964f0fcf3dbff78',
                'method': 'auto',
                'status': 'failure',
                'start_ts': '2018-02-07T22:33:09.582Z',
            },
        }
        if authorize_rc is not None:
            response['verification']['authorize_rc'] = authorize_rc
        return response

    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(),
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'force_cache_invalidate': True,
        },
    )

    extra = {}
    if authorize_rc is not None:
        extra['tech_error_code'] = authorize_rc

    assert response.status_code == 200
    assert response.json() == {
        'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
        'verification': {
            'id': '5cbf6b957c4448ac8964f0fcf3dbff78',
            'method': 'auto',
            'status': 'failure',
            'error_message': error_message,
            **extra,
        },
    }
    assert mock_trust.times_called == 1


@configs.BILLING_SERVICE_NAME
async def test_additional_tech_fields(taxi_cardstorage, mockserver):
    authorize_rc = 'declined_by_issuer'
    authorize_currency = 'ILS'

    @mockserver.json_handler(
        '/trust-lpm/bindings/6cbf6b957c4448ac8964f0fcf3dbff78/verify/',
    )
    def mock_trust(request):
        response = {
            'uid': _UID,
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'verification': {
                'id': '5cbf6b957c4448ac8964f0fcf3dbff78',
                'method': 'auto',
                'status': 'failure',
                'start_ts': '2018-02-07T22:33:09.582Z',
                'authorize_rc': authorize_rc,
                'authorize_currency': authorize_currency,
            },
        }

        return response

    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(),
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'force_cache_invalidate': True,
        },
    )

    assert response.status_code == 200
    verification = response.json()['verification']

    assert verification['tech_error_code'] == authorize_rc
    assert verification['currency'] == authorize_currency

    assert mock_trust.times_called == 1


@configs.BILLING_SERVICE_NAME
async def test_request_binding_429(taxi_cardstorage, mongodb, mockserver, stq):
    @mockserver.json_handler(
        '/trust-lpm/bindings/6cbf6b957c4448ac8964f0fcf3dbff78/verify/',
    )
    def _mock_trust(request):
        assert 'currency' not in request.json
        return mockserver.make_response(
            '',
            429,
            headers={
                'Date': '2018-02-07T22:34:09.582Z',
                'Retry-After': '1234',
            },
        )

    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(),
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'force_cache_invalidate': True,
        },
    )
    assert response.status_code == 429
    assert response.headers['Retry-After'] == '1234'
    assert response.json() == {'error': {'text': 'Too many requests'}}

    assert stq.save_card_verification.times_called == 0
    assert _mock_trust.times_called == 1


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize('code', [404, 422])
async def test_request_binding_with_error(
        taxi_cardstorage, mongodb, mockserver, code, stq,
):
    @mockserver.json_handler(
        '/trust-lpm/bindings/6cbf6b957c4448ac8964f0fcf3dbff78/verify/',
    )
    def _mock_trust(request):
        assert 'currency' not in request.json
        return mockserver.make_response('test error', code)

    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(),
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'force_cache_invalidate': True,
        },
    )
    assert response.status_code == code
    assert response.json() == {'error': {'text': 'test error'}}

    assert stq.save_card_verification.times_called == 0
    assert _mock_trust.times_called == 1


@configs.BILLING_SERVICE_NAME
async def test_race_in_object_creation(
        taxi_cardstorage, mongodb, mockserver, testpoint,
):
    @testpoint('verification_storage::object_creation_race')
    def _verification_storage_testpoint(data):
        mongodb.trust_verifications.insert(
            {
                'uid': _UID,
                'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
                'verification_id': '5cbf6b957c4448ac8964f0fcf3dbff78',
                'method': 'auto',
                'status': '3ds_required',
                'finish_binding_url': 'https://ya.ru',
                '3ds_url': 'https://ya.ru',
                'start_ts': datetime.datetime(2018, 2, 7, 22, 39, 9),
            },
        )

    @mockserver.json_handler(
        '/trust-lpm/bindings/6cbf6b957c4448ac8964f0fcf3dbff78/verify/',
    )
    def _mock_trust(request):
        assert 'currency' not in request.json
        return {
            'uid': _UID,
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'verification': {
                'id': '5cbf6b957c4448ac8964f0fcf3dbff78',
                'method': 'auto',
                'status': 'in_progress',
                'start_ts': '2018-02-07T22:33:09.582Z',
            },
        }

    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(),
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'force_cache_invalidate': True,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
        'verification': {
            'id': '5cbf6b957c4448ac8964f0fcf3dbff78',
            'method': 'auto',
            'status': 'in_progress',
        },
    }
    assert _mock_trust.times_called == 1


@pytest.mark.experiments3(filename='exp3_verification_method.json')
async def _test_verification_method_change(
        taxi_cardstorage,
        mongodb,
        mockserver,
        load_json,
        expected_method,
        afs_response_code,
        num_trust_calls,
        num_afs_calls,
        use_uafs,
):
    @mockserver.json_handler(
        '/trust-lpm/bindings/6cbf6b957c4448ac8964f0fcf3dbff78/verify/',
    )
    def mock_trust(request):
        assert 'currency' not in request.json
        assert json.loads(request.get_data())['method'] == expected_method
        return {
            'uid': _UID,
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'verification': {
                'id': '5cbf6b957c4448ac8964f0fcf3dbff78',
                'method': expected_method,
                'status': 'in_progress',
                'start_ts': '2018-02-07T22:33:09.582Z',
            },
        }

    @mockserver.json_handler('/antifraud/v1/card/verification/type')
    def mock_afs(request):
        expected_request = load_json(
            'test_verification_method_change/afs_request.json',
        )
        assert json.loads(request.get_data()) == expected_request
        if afs_response_code == 200:
            return {'result': 'random_amt'}
        return mockserver.make_response(status=afs_response_code)

    @mockserver.json_handler('/uantifraud/v1/card/verification/type')
    def mock_uafs(request):
        expected_request = load_json(
            'test_verification_method_change/afs_request.json',
        )
        assert json.loads(request.get_data()) == expected_request
        if afs_response_code == 200:
            return {'result': 'random_amt'}
        return mockserver.make_response(status=afs_response_code)

    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(
            login_id='login-id',
            language='ru_RU',
            user_id='user-id',
            pass_flags='pdd,ya-plus',
            personal='personal_phone_id=foobar,personal_email_id=baz',
            bound_uids='1234,5678',
        ),
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'force_cache_invalidate': True,
            'antifraud_payload': {'some_field': 'some_value'},
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
        'verification': {
            'id': '5cbf6b957c4448ac8964f0fcf3dbff78',
            'method': expected_method,
            'status': 'in_progress',
        },
    }
    assert mock_trust.times_called == num_trust_calls

    if use_uafs:
        assert mock_uafs.times_called == num_afs_calls
    else:
        assert mock_afs.times_called == num_afs_calls


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize(
    'expected_method,afs_response_code,num_trust_calls,num_afs_calls',
    [
        pytest.param('standard2_3ds', 200, 1, 0, id='method from experiment'),
        pytest.param(
            'random_amt',
            200,
            1,
            1,
            marks=mark_afs_method(False),
            id='method from AFS',
        ),
        pytest.param(
            'standard2_3ds',
            500,
            1,
            1,
            marks=mark_afs_method(False),
            id='method from AFS error 500',
        ),
        pytest.param(
            'standard2_3ds',
            400,
            1,
            1,
            marks=mark_afs_method(False),
            id='method from AFS error 400',
        ),
    ],
)
@pytest.mark.config(AFS_REQUEST_RETRY=1)
@pytest.mark.config(
    ANTIFRAUD_CLIENT_QOS={
        '__default__': {'attempts': 3, 'timeout-ms': 100},
        '/antifraud/v1/card/verification/type': {
            'attempts': 1,
            'timeout-ms': 100,
        },
    },
)
@pytest.mark.experiments3(filename='exp3_verification_method.json')
async def test_verification_method_change_afs(
        taxi_cardstorage,
        mongodb,
        mockserver,
        load_json,
        expected_method,
        afs_response_code,
        num_trust_calls,
        num_afs_calls,
):
    await _test_verification_method_change(**locals(), use_uafs=False)


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize(
    'expected_method,afs_response_code,num_trust_calls,num_afs_calls',
    [
        pytest.param('standard2_3ds', 200, 1, 0, id='method from experiment'),
        pytest.param(
            'random_amt',
            200,
            1,
            1,
            marks=mark_afs_method(True),
            id='method from AFS',
        ),
        pytest.param(
            'standard2_3ds',
            500,
            1,
            1,
            marks=mark_afs_method(True),
            id='method from AFS error 500',
        ),
        pytest.param(
            'standard2_3ds',
            400,
            1,
            1,
            marks=mark_afs_method(True),
            id='method from AFS error 400',
        ),
    ],
)
@pytest.mark.config(
    UANTIFRAUD_CLIENT_QOS={
        '__default__': {'attempts': 3, 'timeout-ms': 100},
        '/uantifraud/v1/card/verification/type': {
            'attempts': 1,
            'timeout-ms': 100,
        },
    },
)
@pytest.mark.experiments3(filename='exp3_verification_method.json')
async def test_verification_method_change_uafs(
        taxi_cardstorage,
        mongodb,
        mockserver,
        load_json,
        expected_method,
        afs_response_code,
        num_trust_calls,
        num_afs_calls,
):
    await _test_verification_method_change(**locals(), use_uafs=True)


@configs.BILLING_SERVICE_NAME
@pytest.mark.config(CARDSTORAGE_CHECK_CACHE_BEFORE_VERIFICATION=True)
async def test_fail_on_verified_card(taxi_cardstorage):
    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(),
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': 'card-x2345b3e693972872b9b58946',
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'binding_id': 'card-x2345b3e693972872b9b58946',
        'verification': {
            'id': 'invalid',
            'method': 'standard2',
            'status': 'failure',
        },
    }


@configs.BILLING_SERVICE_NAME
@pytest.mark.config(CARDSTORAGE_CHECK_CACHE_BEFORE_VERIFICATION=True)
async def test_success_on_unbound_card(taxi_cardstorage, mockserver):
    @mockserver.json_handler(
        '/trust-lpm/bindings/card-x2345b3e693972872b9b58947/verify/',
    )
    def _mock_trust(request):
        assert 'currency' not in request.json
        return {
            'uid': _UID,
            'binding_id': 'card-x2345b3e693972872b9b58947',
            'verification': {
                'id': '5cbf6b957c4448ac8964f0fcf3dbff78',
                'method': 'standard2_3ds',
                'status': 'in_progress',
                'start_ts': '2018-02-07T22:33:09.582Z',
            },
        }

    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(),
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': 'card-x2345b3e693972872b9b58947',
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'binding_id': 'card-x2345b3e693972872b9b58947',
        'verification': {
            'id': '5cbf6b957c4448ac8964f0fcf3dbff78',
            'method': 'standard2_3ds',
            'status': 'in_progress',
        },
    }
    assert _mock_trust.times_called == 1


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize(
    'payload,expected_currency',
    [
        ({'card_number': '123456****789'}, 'UZS'),
        ({'card_number': '654321****987'}, None),
    ],
)
@pytest.mark.config(
    CARDSTORAGE_DETECT_VERIFICATION_CURRENCY_ALGO='by_bin',
    CARDSTORAGE_BIN_INFO={'123456': {'currency': 'UZS'}},
)
async def test_detect_currency_by_bin(
        taxi_cardstorage, mockserver, payload, expected_currency,
):
    @mockserver.json_handler('/trust-lpm/bindings/card-x1234/verify/')
    def _mock_trust(request):
        if expected_currency is None:
            assert 'currency' not in request.json
        else:
            assert request.json['currency'] == expected_currency
        return {
            'uid': _UID,
            'binding_id': 'card-x1234',
            'verification': {
                'id': 'deadf00d',
                'method': 'standard2_3ds',
                'status': 'in_progress',
                'start_ts': '2018-02-07T22:33:09.582Z',
            },
        }

    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(),
        json={'binding_id': 'card-x1234', 'antifraud_payload': payload},
    )

    assert response.status_code == 200
    assert response.json() == {
        'binding_id': 'card-x1234',
        'verification': {
            'id': 'deadf00d',
            'method': 'standard2_3ds',
            'status': 'in_progress',
        },
    }
    assert _mock_trust.times_called == 1


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize('request_currency', ['ILS', None])
async def test_currency_from_request(
        taxi_cardstorage, mockserver, request_currency,
):
    @mockserver.json_handler('/trust-lpm/bindings/card-x1234/verify/')
    def _mock_trust(request):
        if request_currency is None:
            assert 'currency' not in request.json
        else:
            assert request.json['currency'] == request_currency
        return {
            'uid': _UID,
            'binding_id': 'card-x1234',
            'verification': {
                'id': 'deadf00d',
                'method': 'standard2_3ds',
                'status': 'in_progress',
                'start_ts': '2018-02-07T22:33:09.582Z',
            },
        }

    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(),
        json={'binding_id': 'card-x1234', 'currency': request_currency},
    )

    assert response.status_code == 200
    assert _mock_trust.times_called == 1


@pytest.mark.experiments3(
    name='payment_billing_service_name',
    consumers=['cardstorage/payment_verifications'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'region 100',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 100,
                    'arg_name': 'region_id',
                    'arg_type': 'int',
                },
            },
            'value': {'service_name': 'uber'},
        },
        {
            'title': 'country_iso2 FR',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'FR',
                    'arg_name': 'country_iso2',
                    'arg_type': 'string',
                },
            },
            'value': {'service_name': 'grocery'},
        },
    ],
    default_value={'service_name': 'card'},
    is_config=True,
)
@pytest.mark.parametrize(
    'region_id, country_iso2, token',
    [
        (100, 'RU', 'ubertaxi_4ea0f5fc283dc942c27bc7ae022e8821'),
        (101, 'FR', 'lavka_delivery_b8837be388d39db7df042182ca0315f7'),
        (102, 'GB', 'taxifee_8c7078d6b3334e03c1b4005b02da30f4'),
    ],
)
async def test_payment_billing_service_name_exp_kwargs(
        taxi_cardstorage, mockserver, region_id, country_iso2, token,
):
    @mockserver.json_handler(
        '/trust-lpm/bindings/card-x2345b3e693972872b9b58947/verify/',
    )
    def _mock_trust(request):
        assert request.headers['X-Service-Token'] == token
        return {
            'uid': _UID,
            'binding_id': 'card-x2345b3e693972872b9b58947',
            'verification': {
                'id': '5cbf6b957c4448ac8964f0fcf3dbff78',
                'method': 'standard2_3ds',
                'status': 'in_progress',
                'start_ts': '2018-02-07T22:33:09.582Z',
            },
        }

    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(),
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': 'card-x2345b3e693972872b9b58947',
            'region_id': region_id,
            'country_iso2': country_iso2,
        },
    )

    assert _mock_trust.times_called == 1

    assert response.status_code == 200


@configs.BILLING_SERVICE_NAME
async def test_request_billing_service_name(taxi_cardstorage, mockserver):
    @mockserver.json_handler(
        '/trust-lpm/bindings/card-x2345b3e693972872b9b58947/verify/',
    )
    def _mock_trust(request):
        assert (
            request.headers['X-Service-Token']
            == 'lavka_delivery_b8837be388d39db7df042182ca0315f7'
        )
        return {
            'uid': _UID,
            'binding_id': 'card-x2345b3e693972872b9b58947',
            'verification': {
                'id': '5cbf6b957c4448ac8964f0fcf3dbff78',
                'method': 'standard2_3ds',
                'status': 'in_progress',
                'start_ts': '2018-02-07T22:33:09.582Z',
            },
        }

    response = await taxi_cardstorage.post(
        '/v1/payment_verifications',
        headers=get_headers(),
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': 'card-x2345b3e693972872b9b58947',
            'region_id': 101,
            'country_iso2': 'FR',
            'billing_service': 'grocery',
        },
    )

    assert _mock_trust.times_called == 1

    assert response.status_code == 200
