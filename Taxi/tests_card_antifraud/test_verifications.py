import json

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_card_antifraud import configs


PATH_PARAMS = [
    ('/4.0/payment/verifications', True),
    ('/4.0/payment/v2/verifications', False),
]

YANDEX_UID = '1234'
CARD_ID = 'card-x1234567'

DEVICE_ID_1 = 'device-id-1'
DEVICE_ID_2 = 'device-id-2'

IDEMPOTENCY_TOKEN = 'some-token'

USER_API_404 = {'code': '404', 'message': 'No user with id '}

TRUST_START_VERIFY_RESPONSE = {
    'uid': YANDEX_UID,
    'binding_id': CARD_ID,
    'verification': {
        'id': 'temp_id',
        'method': 'random_amt',
        'status': 'amount_expected',
        'tries_left': 3,
        'start_ts': '2018-05-15T20:24:06.785000+03:00',
        'authorize_currency': 'RUB',
    },
}


@pytest.fixture(autouse=True)
def mock_afs(mockserver):
    @mockserver.json_handler('/antifraud/v1/card/verification/type')
    def _mock_afs(request):
        return mockserver.make_response('{}', 500)


def select_verifications(
        pgsql, user_uid, device_id, card_id, idempotency_token, uses_device_id,
):
    device_id = device_id if uses_device_id else ''

    cursor = pgsql['card_antifraud'].cursor()
    cursor.execute(
        (
            f'SELECT * '
            f'FROM card_antifraud.cards_verification '
            f'WHERE yandex_uid = \'{user_uid}\''
            f'AND device_id = \'{device_id}\''
            f'AND card_id = \'{card_id}\''
            f'AND idempotency_token = \'{idempotency_token}\''
        ),
    )
    columns = [it.name for it in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor]
    return rows


def get_query_params(
        uid='1234',
        card_id='card-x1234567',
        token=IDEMPOTENCY_TOKEN,
        brand='yataxi',
        region_id=200,
        country_iso2='RU',
        device_id=None,
        currency=None,
):
    return (
        {
            'card_id': card_id,
            'region_id': region_id,
            'country_iso2': country_iso2,
            'currency': currency,
        },
        {
            'X-Yandex-Uid': uid,
            'X-YaTaxi-UserId': 'user_id',
            'X-Remote-IP': '127.0.0.1',
            'X-Idempotency-Token': token,
            'X-Login-Id': 't:login_id',
            'X-Request-Application': 'app_name=android,app_brand=' + brand,
            'X-YaTaxi-Bound-Uids': '1,2,3',
            'X-Request-Language': 'en',
            'X-YaTaxi-Pass-Flags': 'portal',
            'X-AppMetrica-DeviceId': device_id,
        },
    )


async def make_request(
        path, taxi_card_antifraud, request_body, headers, code=200, body=None,
):
    response = await taxi_card_antifraud.post(
        path, request_body, headers=headers,
    )
    assert response.status_code == code
    if body is not None:
        assert response.json() == body
    return response


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize('path, uses_device_id', PATH_PARAMS)
@pytest.mark.experiments3(filename='experiments3_verificate_currency.json')
async def test_full_flow_success(
        taxi_card_antifraud,
        pgsql,
        mockserver,
        taxi_card_antifraud_monitor,
        path,
        uses_device_id,
):
    uid, card_id, token = ('1234', 'card-x1234567', 'test_key')

    @mockserver.json_handler('/cardstorage/v1/card')
    def _mock_cardstorage(request):
        return {
            'card_id': '1',
            'billing_card_id': '1',
            'permanent_card_id': '1',
            'currency': 'RUB',
            'expiration_month': 12,
            'expiration_year': 2020,
            'owner': 'Mr',
            'possible_moneyless': False,
            'region_id': 'RU',
            'regions_checked': ['RU'],
            'system': 'VISA',
            'valid': True,
            'bound': True,
            'unverified': False,
            'busy': False,
            'busy_with': [],
            'from_db': True,
            'number': '5100222233334444',
        }

    @mockserver.json_handler(
        (
            '/yb-trust-paysys/bindings-external/v2.0'
            '/bindings/card-x1234567/verify/'
        ),
    )
    def _mock_verify(request):
        assert request.json['method'] == 'standard2'
        assert request.json['wait_for_cvn'] is True
        assert request.json['currency'] == 'RUB'
        assert request.headers.get('X-Login-Id') == 't:login_id'
        return {
            'uid': uid,
            'binding_id': card_id,
            'verification': {
                'id': 'temp_id',
                'method': 'standard2',
                'status': 'in_progress',
                'start_ts': '2018-05-15T20:24:06.785000+03:00',
                'authorize_currency': 'RUB',
            },
        }

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users(request):
        assert 'id' in request.json
        assert request.json['id'] == 'user_id'
        return {'id': 'user_id', 'metrica_device_id': 'temporary_id'}

    pg_result = select_verifications(
        pgsql, uid, 'temporary_id', card_id, token, uses_device_id,
    )
    assert not pg_result

    request_body, headers = get_query_params(uid, card_id, token)

    async with metrics_helpers.MetricsCollector(
            taxi_card_antifraud_monitor,
            sensor='verification_start',
            labels={
                'verification_method': 'standard2',
                'is_wait_for_cvn': '1',
                'currency': 'RUB',
                'user_application': 'android',
            },
    ) as collector:
        response = await make_request(
            path, taxi_card_antifraud, request_body, headers,
        )

    assert response.json() == {
        'purchase_token': 'temp_id',
        'verification_id': 'temp_id',
    }

    pg_result = select_verifications(
        pgsql, uid, 'temporary_id', card_id, token, uses_device_id,
    )
    assert len(pg_result) == 1

    verification = pg_result[0]
    assert verification['status'] == 'in_progress'
    assert verification['version'] == 1

    assert collector.get_single_collected_metric().value == 1


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize('path, uses_device_id', PATH_PARAMS)
@pytest.mark.experiments3(filename='experiments3_3ds.json')
async def test_3ds(
        taxi_card_antifraud, pgsql, mockserver, path, uses_device_id,
):
    uid, card_id, token = ('1234', 'card-x1234567', 'test_key')

    @mockserver.json_handler(
        (
            '/yb-trust-paysys/bindings-external/v2.0'
            '/bindings/card-x1234567/verify/'
        ),
    )
    def _mock_verify(request):
        assert request.json['method'] == 'standard2_3ds'
        assert request.json['wait_for_cvn'] is False
        return {
            'uid': uid,
            'binding_id': card_id,
            'verification': {
                'id': 'temp_id',
                'method': 'standard2_3ds',
                'status': '3ds_required',
                '3ds_url': 'some_3ds_url',
                'finish_binding_url': 'some_finish_binding_url',
                'start_ts': '2018-05-15T20:24:06.785000+03:00',
                'authorize_currency': 'RUB',
            },
        }

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users(request):
        assert 'id' in request.json
        assert request.json['id'] == 'user_id'
        return {'id': 'user_id', 'metrica_device_id': 'temporary_id'}

    pg_result = select_verifications(
        pgsql, uid, 'temporary_id', card_id, token, uses_device_id,
    )
    assert not pg_result

    request_body, headers = get_query_params(uid, card_id, token)

    response = await make_request(
        path, taxi_card_antifraud, request_body, headers,
    )
    assert response.json() == {
        'purchase_token': 'temp_id',
        'verification_id': 'temp_id',
    }

    pg_result = select_verifications(
        pgsql, uid, 'temporary_id', card_id, token, uses_device_id,
    )
    assert len(pg_result) == 1

    verification = pg_result[0]
    assert verification['status'] == '3ds_required'
    assert verification['version'] == 1
    assert verification['x3ds_url'] == 'some_3ds_url'
    assert verification['finish_binding_url'] == 'some_finish_binding_url'


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize('path, uses_device_id', PATH_PARAMS)
async def test_user_api_failure(
        taxi_card_antifraud, pgsql, mockserver, path, uses_device_id,
):
    uid, card_id, token = ('1234', 'card-x1234567', 'test_key')

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users(request):
        return {'id': 'user_id'}

    request_body, headers = get_query_params(uid, card_id, token)
    if uses_device_id:
        await make_request(
            path, taxi_card_antifraud, request_body, headers, 409,
        )


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize('path, uses_device_id', PATH_PARAMS)
async def test_trust_failure(
        taxi_card_antifraud, pgsql, mockserver, path, uses_device_id,
):
    uid, card_id, token = ('1234', 'card-x1234567', 'test_key')

    @mockserver.json_handler(
        (
            '/yb-trust-paysys/bindings-external/v2.0'
            '/bindings/card-x1234567/verify/'
        ),
    )
    def _mock_verify(request):
        return mockserver.make_response('', 500)

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users(request):
        return {'id': 'user_id', 'metrica_device_id': 'temporary_id'}

    pg_result = select_verifications(
        pgsql, uid, 'temporary_id', card_id, token, uses_device_id,
    )
    assert not pg_result

    request_body, headers = get_query_params(uid, card_id, token)
    await make_request(path, taxi_card_antifraud, request_body, headers, 500)

    pg_result = select_verifications(
        pgsql, uid, 'temporary_id', card_id, token, uses_device_id,
    )
    assert len(pg_result) == 1
    assert pg_result[0]['status'] == 'draft'


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize('path, uses_device_id', PATH_PARAMS)
async def test_already_in_progress(
        taxi_card_antifraud, pgsql, mockserver, path, uses_device_id,
):
    uid, card_id, token = ('1235', 'card-x1234568', 'test_token')

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users(request):
        return {'id': 'user_id', 'metrica_device_id': 'test_id'}

    pg_result = select_verifications(
        pgsql, uid, 'test_id', card_id, token, uses_device_id,
    )
    assert len(pg_result) == 1
    assert pg_result[0]['status'] == 'in_progress'
    assert pg_result[0]['version'] == 1

    request_body, headers = get_query_params(uid, card_id, token)
    response = await make_request(
        path, taxi_card_antifraud, request_body, headers,
    )
    assert response.json() == {
        'purchase_token': 'temp_id1',
        'verification_id': 'temp_id1',
    }

    pg_result = select_verifications(
        pgsql, uid, 'test_id', card_id, token, uses_device_id,
    )
    assert len(pg_result) == 1
    assert pg_result[0]['status'] == 'in_progress'
    assert pg_result[0]['version'] == 1


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize('path, uses_device_id', PATH_PARAMS)
async def test_invalid_in_db(
        taxi_card_antifraud, pgsql, mockserver, path, uses_device_id,
):
    uid, card_id, token = ('1236', 'card-x1234568', 'test_token')

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users(request):
        return {'id': 'user_id', 'metrica_device_id': 'test_id'}

    request_body, headers = get_query_params(uid, card_id, token)
    await make_request(path, taxi_card_antifraud, request_body, headers, 500)


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize('path, uses_device_id', PATH_PARAMS)
async def test_commit_existing_draft(
        taxi_card_antifraud, pgsql, mockserver, path, uses_device_id,
):
    uid, card_id, token = ('1235', 'card-x1234567', 'test_token1')

    @mockserver.json_handler(
        (
            '/yb-trust-paysys/bindings-external/v2.0'
            '/bindings/card-x1234567/verify/'
        ),
    )
    def _mock_verify(request):
        return {
            'uid': uid,
            'binding_id': card_id,
            'verification': {
                'id': 'temp_id',
                'method': 'standard2_3ds',
                'status': 'in_progress',
                'start_ts': '2018-05-15T20:24:06.785000+03:00',
                'authorize_currency': 'RUB',
            },
        }

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users(request):
        return {'id': 'user_id', 'metrica_device_id': 'test_id'}

    pg_result = select_verifications(
        pgsql, uid, 'test_id', card_id, token, uses_device_id,
    )
    assert len(pg_result) == 1
    assert pg_result[0]['status'] == 'draft'

    request_body, headers = get_query_params(uid, card_id, token)
    response = await make_request(
        path, taxi_card_antifraud, request_body, headers,
    )
    assert response.json() == {
        'purchase_token': 'temp_id',
        'verification_id': 'temp_id',
    }

    pg_result = select_verifications(
        pgsql, uid, 'test_id', card_id, token, uses_device_id,
    )
    assert len(pg_result) == 1
    assert pg_result[0]['status'] == 'in_progress'


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize('path, uses_device_id', PATH_PARAMS)
@pytest.mark.config(CARD_ANTIFRAUD_SERVICE_ENABLED=False)
async def test_verifications_service_disabled(
        taxi_card_antifraud, path, uses_device_id,
):
    uid, card_id, token = ('1235', 'card-x1234567', 'test_token1')
    request_body, headers = get_query_params(uid, card_id, token)
    await make_request(path, taxi_card_antifraud, request_body, headers, 429)


async def _test_antifraud(
        taxi_card_antifraud, pgsql, mockserver, path, uses_device_id, is_uafs,
):
    token = 'test_key'

    @mockserver.json_handler(
        (
            '/yb-trust-paysys/bindings-external/v2.0'
            '/bindings/card-x1234567/verify/'
        ),
    )
    def _mock_verify(request):
        assert request.json['method'] == 'random_amt'
        assert request.json['wait_for_cvn'] is False
        return TRUST_START_VERIFY_RESPONSE

    @mockserver.json_handler('/antifraud/v1/card/verification/type')
    def _mock_afs(request):
        assert request.json == {
            'application': 'android',
            'bound_uids': '1,2,3',
            'language': 'en',
            'login_id': 't:login_id',
            'pass_flags': 'portal',
            'passport_uid': YANDEX_UID,
            'service_id': 'card',
            'type': 'additional',
            'user': '',
            'user_id': 'user_id',
            'user_ip': '127.0.0.1',
        }
        return {'result': 'random_amt'}

    @mockserver.json_handler('/uantifraud/v1/card/verification/type')
    def _mock_uafs(request):
        assert request.json == {
            'application': 'android',
            'bound_uids': '1,2,3',
            'language': 'en',
            'login_id': 't:login_id',
            'pass_flags': 'portal',
            'passport_uid': YANDEX_UID,
            'service_id': 'card',
            'type': 'additional',
            'user': '',
            'user_id': 'user_id',
            'user_ip': '127.0.0.1',
        }
        return {'result': 'random_amt'}

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users(request):
        assert 'id' in request.json
        assert request.json['id'] == 'user_id'
        return {'id': 'user_id', 'metrica_device_id': 'temporary_id'}

    pg_result = select_verifications(
        pgsql, YANDEX_UID, 'temporary_id', CARD_ID, token, uses_device_id,
    )
    assert not pg_result

    request_body, headers = get_query_params(YANDEX_UID, CARD_ID, token)

    response = await make_request(
        path, taxi_card_antifraud, request_body, headers,
    )
    assert response.json() == {
        'purchase_token': 'temp_id',
        'verification_id': 'temp_id',
    }

    if is_uafs:
        assert await _mock_uafs.wait_call()
    else:
        assert await _mock_afs.wait_call()

    pg_result = select_verifications(
        pgsql, YANDEX_UID, 'temporary_id', CARD_ID, token, uses_device_id,
    )
    assert len(pg_result) == 1

    verification = pg_result[0]
    assert verification['status'] == 'amount_expected'
    assert verification['version'] == 1


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize('path, uses_device_id', PATH_PARAMS)
@pytest.mark.experiments3(filename='experiments3_3ds.json')
async def test_afs(
        taxi_card_antifraud, pgsql, mockserver, path, uses_device_id,
):
    await _test_antifraud(
        taxi_card_antifraud, pgsql, mockserver, path, uses_device_id, False,
    )


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize('path, uses_device_id', PATH_PARAMS)
@pytest.mark.experiments3(filename='experiments3_3ds.json')
@pytest.mark.config(UAFS_CARD_ANTIFRAUD_CHANGE_VERIFY_TYPE_DEST=True)
async def test_uafs(
        taxi_card_antifraud, pgsql, mockserver, path, uses_device_id,
):
    await _test_antifraud(
        taxi_card_antifraud, pgsql, mockserver, path, uses_device_id, True,
    )


@pytest.mark.parametrize('path, uses_device_id', PATH_PARAMS)
@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize('processing_name', [None, configs.PROCESSING_NAME])
async def test_processing_name(
        taxi_card_antifraud,
        mockserver,
        path,
        uses_device_id,
        processing_name,
        experiments3,
):
    if processing_name:
        experiments3.add_config(
            name='binding_processing_name',
            consumers=['cardantifraud'],
            default_value={'processing_name': processing_name},
        )

    @mockserver.json_handler(
        '/yb-trust-paysys/bindings-external/v2.0/bindings/{}/verify/'.format(
            CARD_ID,
        ),
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

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users(request):
        return {'id': 'user_id', 'metrica_device_id': 'temporary_id'}

    request_body, headers = get_query_params(uid=YANDEX_UID, card_id=CARD_ID)

    response = await make_request(
        path, taxi_card_antifraud, request_body, headers,
    )

    assert response.status_code == 200
    assert mock_trust.times_called == 1


@pytest.mark.parametrize('path, uses_device_id', PATH_PARAMS)
@configs.CARDSTORAGE_AVS_DATA
@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize(
    'pass_params, post_code, street_address',
    [
        (False, configs.AVS_POST_CODE, configs.AVS_STREET_ADDRESS),
        (
            True,
            configs.AVS_POST_CODE + '_1',
            configs.AVS_STREET_ADDRESS + '_1',
        ),
    ],
)
async def test_avs_data_in_pass_params(
        taxi_card_antifraud,
        mockserver,
        path,
        uses_device_id,
        pass_params,
        post_code,
        street_address,
):
    @mockserver.json_handler(
        '/yb-trust-paysys/bindings-external/v2.0/bindings/{}/verify/'.format(
            CARD_ID,
        ),
    )
    def mock_trust(request):
        pass_params = request.json['pass_params']
        avs_data = pass_params['avs_data']
        assert avs_data == {
            'avs_post_code': post_code,
            'avs_street_address': street_address,
        }

        return TRUST_START_VERIFY_RESPONSE

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users(request):
        return {'id': 'user_id', 'metrica_device_id': 'temporary_id'}

    request_body, headers = get_query_params(uid=YANDEX_UID, card_id=CARD_ID)

    if pass_params:
        request_body['pass_params'] = {
            'avs_data': {
                'post_code': post_code,
                'street_address': street_address,
            },
        }

    response = await make_request(
        path, taxi_card_antifraud, request_body, headers,
    )

    assert response.status_code == 200
    assert mock_trust.times_called == 1


@pytest.mark.parametrize('path, uses_device_id', PATH_PARAMS)
@configs.CARDSTORAGE_AVS_DATA
@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize('request_currency', ['ILS', None])
async def test_currency_request(
        taxi_card_antifraud,
        mockserver,
        path,
        uses_device_id,
        request_currency,
):
    @mockserver.json_handler(
        '/yb-trust-paysys/bindings-external/v2.0/bindings/{}/verify/'.format(
            CARD_ID,
        ),
    )
    def mock_trust(request):
        if request_currency is not None:
            assert request.json['currency'] == request_currency
        else:
            assert 'currency' not in request.json

        return TRUST_START_VERIFY_RESPONSE

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users(request):
        return {'id': 'user_id', 'metrica_device_id': 'temporary_id'}

    request_body, headers = get_query_params(
        uid=YANDEX_UID, card_id=CARD_ID, currency=request_currency,
    )

    response = await make_request(
        path, taxi_card_antifraud, request_body, headers,
    )

    assert response.status_code == 200
    assert mock_trust.times_called == 1


@pytest.mark.parametrize('path, uses_device_id', PATH_PARAMS)
@configs.BINDING_RETURN_PATH_URL
@configs.BILLING_SERVICE_NAME
async def test_return_path(
        taxi_card_antifraud, mockserver, path, uses_device_id,
):
    @mockserver.json_handler(
        '/yb-trust-paysys/bindings-external/v2.0/bindings/{}/verify/'.format(
            CARD_ID,
        ),
    )
    def mock_trust(request):
        return_path = request.json['return_path']
        assert return_path == configs.RETURN_PATH

        return TRUST_START_VERIFY_RESPONSE

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users(request):
        return {'id': 'user_id', 'metrica_device_id': 'temporary_id'}

    request_body, headers = get_query_params(uid=YANDEX_UID, card_id=CARD_ID)

    response = await make_request(
        path, taxi_card_antifraud, request_body, headers,
    )

    assert response.status_code == 200
    assert mock_trust.times_called == 1


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize('path, uses_device_id', PATH_PARAMS)
@pytest.mark.parametrize(
    'brand, expected_token',
    [
        ('yataxi', 'taxifee_8c7078d6b3334e03c1b4005b02da30f4'),
        ('yango', 'taxifee_8c7078d6b3334e03c1b4005b02da30f4'),
        ('yauber', 'ubertaxi_4ea0f5fc283dc942c27bc7ae022e8821'),
    ],
)
async def test_service_token(
        taxi_card_antifraud,
        mockserver,
        path,
        uses_device_id,
        brand,
        expected_token,
):
    @mockserver.json_handler(
        '/yb-trust-paysys/bindings-external/v2.0/bindings/{}/verify/'.format(
            CARD_ID,
        ),
    )
    def mock_trust(request):
        assert request.headers['X-Service-Token'] == expected_token

        return TRUST_START_VERIFY_RESPONSE

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users(request):
        return {'id': 'user_id', 'metrica_device_id': 'temporary_id'}

    request_body, headers = get_query_params(
        uid=YANDEX_UID, card_id=CARD_ID, brand=brand,
    )

    response = await make_request(
        path, taxi_card_antifraud, request_body, headers,
    )

    assert response.status_code == 200
    assert mock_trust.times_called == 1


@pytest.mark.experiments3(
    name='payment_billing_service_name',
    consumers=['cardantifraud'],
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
@pytest.mark.parametrize('path, uses_device_id', PATH_PARAMS)
@pytest.mark.parametrize(
    'region_id, country_iso2, expected_token',
    [
        (101, 'IS', 'taxifee_8c7078d6b3334e03c1b4005b02da30f4'),
        (102, 'FR', 'lavka_delivery_b8837be388d39db7df042182ca0315f7'),
        (100, 'RU', 'ubertaxi_4ea0f5fc283dc942c27bc7ae022e8821'),
    ],
)
async def test_payment_billing_service_name_exp_kwargs(
        taxi_card_antifraud,
        mockserver,
        path,
        uses_device_id,
        region_id,
        country_iso2,
        expected_token,
):
    @mockserver.json_handler(
        '/yb-trust-paysys/bindings-external/v2.0/bindings/{}/verify/'.format(
            CARD_ID,
        ),
    )
    def mock_trust(request):
        assert request.headers['X-Service-Token'] == expected_token

        return TRUST_START_VERIFY_RESPONSE

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users(request):
        return {'id': 'user_id', 'metrica_device_id': 'temporary_id'}

    request_body, headers = get_query_params(
        uid=YANDEX_UID,
        card_id=CARD_ID,
        region_id=region_id,
        country_iso2=country_iso2,
    )

    response = await make_request(
        path, taxi_card_antifraud, request_body, headers,
    )

    assert response.status_code == 200
    assert mock_trust.times_called == 1


@configs.BILLING_SERVICE_NAME
@pytest.mark.parametrize(
    'data',
    [
        pytest.param(
            dict(
                use_header_device_id=True,
                user_api_device_id=DEVICE_ID_1,
                header_device_id=DEVICE_ID_1,
                pg_device_id=DEVICE_ID_1,
                status_code=200,
            ),
            id='equal_device_ids',
        ),
        pytest.param(
            dict(
                use_header_device_id=True,
                user_api_device_id=DEVICE_ID_1,
                header_device_id=DEVICE_ID_2,
                pg_device_id=DEVICE_ID_1,
                status_code=200,
            ),
            id='another_header_device_id_should_use_from_user_api',
        ),
        pytest.param(
            dict(
                use_header_device_id=True,
                user_api_device_id=DEVICE_ID_1,
                header_device_id=None,
                pg_device_id=DEVICE_ID_1,
                status_code=200,
            ),
            id='use_user_api_device_id_if_null_header_and_enabled_config',
        ),
        pytest.param(
            dict(
                use_header_device_id=False,
                user_api_device_id=DEVICE_ID_1,
                header_device_id=None,
                pg_device_id=DEVICE_ID_1,
                status_code=200,
            ),
            id='use_user_api_device_id_if_null_header_and_disabled_config',
        ),
        pytest.param(
            dict(
                use_header_device_id=True,
                user_api_device_id=None,
                header_device_id=DEVICE_ID_1,
                pg_device_id=DEVICE_ID_1,
                status_code=200,
            ),
            id='use_header_device_id_if_null_from_user_api',
        ),
        pytest.param(
            dict(
                use_header_device_id=False,
                user_api_device_id=None,
                header_device_id=DEVICE_ID_1,
                pg_device_id=DEVICE_ID_1,
                status_code=409,
            ),
            id='409_if_null_from_user_api_and_disabled_config',
        ),
    ],
)
async def test_header_device_id(
        taxi_card_antifraud, mockserver, pgsql, experiments3, data,
):
    use_header_device_id = data['use_header_device_id']
    user_api_device_id = data['user_api_device_id']
    header_device_id = data['header_device_id']
    pg_device_id = data['pg_device_id']
    status_code = data['status_code']

    @mockserver.json_handler(
        '/yb-trust-paysys/bindings-external/v2.0/bindings/{}/verify/'.format(
            CARD_ID,
        ),
    )
    def _mock_trust(request):
        return TRUST_START_VERIFY_RESPONSE

    configs.use_header_device_id(experiments3, enabled=use_header_device_id)

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users(request):
        if user_api_device_id is None:
            return mockserver.make_response(json.dumps(USER_API_404), 404)

        return {'id': 'user_id', 'metrica_device_id': user_api_device_id}

    request_body, headers = get_query_params(
        uid=YANDEX_UID, card_id=CARD_ID, device_id=header_device_id,
    )

    await make_request(
        '/4.0/payment/verifications',
        taxi_card_antifraud,
        request_body,
        headers,
        code=status_code,
    )

    pg_result = select_verifications(
        pgsql,
        YANDEX_UID,
        pg_device_id,
        CARD_ID,
        IDEMPOTENCY_TOKEN,
        uses_device_id=True,
    )
    assert len(pg_result) == int(status_code == 200)
