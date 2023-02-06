import json

import pytest

from protocol import brands


@pytest.fixture
def getreferral_services(mockserver):
    class context:
        uid = '4003514353'

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return {
            'uid': {'value': context.uid},
            'status': {'value': 'VALID'},
            'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
            'aliases': {'10': 'phonish'},
            'phones': [
                {'attributes': {'102': '+79998887766'}, 'id': '1111'},
                {
                    'attributes': {'102': '+72222222222', '107': '1'},
                    'id': '2222',
                },
            ],
        }

    return context


def test_invalid_id(taxi_protocol, getreferral_services):
    getreferral_services.uid = '4003514356'
    response = taxi_protocol.post(
        '3.0/getreferral',
        json={'id': 'some_invalid_id', 'format_currency': True},
        bearer='test_token',
    )
    assert response.status_code == 401


def test_invalid_id2(taxi_protocol, getreferral_services):
    getreferral_services.uid = '4003514356'
    response = taxi_protocol.post(
        '3.0/getreferral',
        json={'id': [], 'format_currency': True},
        bearer='test_token',
    )
    assert response.status_code == 400


def test_invalid_format_currency(taxi_protocol, getreferral_services):
    getreferral_services.uid = '4003514356'
    response = taxi_protocol.post(
        '3.0/getreferral',
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef19',
            'format_currency': 'some string',
        },
        bearer='test_token',
    )
    assert response.status_code == 400


def test_user_no_phone(taxi_protocol, getreferral_services):
    getreferral_services.uid = '4003514357'
    response = taxi_protocol.post(
        '3.0/getreferral',
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef20',
            'format_currency': True,
        },
        bearer='test_token',
    )
    assert response.status_code == 406


def test_user_no_city(taxi_protocol, getreferral_services):
    getreferral_services.uid = '4003514358'
    response = taxi_protocol.post(
        '3.0/getreferral',
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef21',
            'format_currency': True,
        },
        bearer='test_token',
    )
    assert response.status_code == 406


TEST_USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'


@pytest.mark.config(REFERRALS_ENABLED_BY_BRAND=['yataxi'])
@pytest.mark.parametrize(
    'useragent, status_code',
    [(brands._UA_YANDEX_TAXI_ANDROID, 200), (brands._UA_YAUBER_ANDROID, 406)],
)
def test_enabled_by_brand(
        taxi_protocol,
        mockserver,
        getreferral_services,
        useragent,
        status_code,
):
    @mockserver.handler('/coupons/v1/coupons/referral')
    def mock_coupons_getreferral(request):
        return mockserver.make_response('[]', 200)

    response = taxi_protocol.post(
        '3.0/getreferral',
        json={'id': TEST_USER_ID},
        bearer='test_token',
        headers={'User-Agent': useragent},
    )
    assert mock_coupons_getreferral.times_called == (status_code == 200)
    assert response.status_code == status_code


def test_getrefferal_via_coupons(
        tvm2_client, taxi_protocol, mockserver, getreferral_services,
):
    """
    Tests that coupons service is getting called with tvm.
    """
    ticket = 'secret'
    tvm2_client.set_ticket(json.dumps({'40': {'ticket': ticket}}))

    @mockserver.handler('/coupons/v1/coupons/referral')
    def mock_coupons_getreferral(request):
        assert request.headers['X-Ya-Service-Ticket'] == ticket
        return mockserver.make_response('', 200)

    taxi_protocol.post(
        '3.0/getreferral', json={'id': TEST_USER_ID}, bearer='test_token',
    )

    assert mock_coupons_getreferral.times_called == 1


@pytest.mark.parametrize(
    'source_json, expected_format_currency',
    [
        ({'id': TEST_USER_ID}, False),
        ({'id': TEST_USER_ID, 'format_currency': False}, False),
        ({'id': TEST_USER_ID, 'format_currency': True}, True),
    ],
)
def test_getrefferal_via_coupons_request_format(
        source_json,
        expected_format_currency,
        taxi_protocol,
        mockserver,
        getreferral_services,
):
    """
    Tests the format of request to the coupons service.
    """
    call_info = {}

    @mockserver.handler('/coupons/v1/coupons/referral')
    def mock_coupons_getreferral(request):
        call_info['json'] = request.json
        return mockserver.make_response('', 200)

    taxi_protocol.post(
        '3.0/getreferral', json=source_json, bearer='test_token',
    )

    assert call_info['json'] == {
        'yandex_uid': '4003514353',
        'phone_id': '5714f45e98956f06baaae3d4',
        'zone_name': 'moscow',
        'locale': 'en',
        'country': 'rus',
        'currency': 'RUB',
        'format_currency': expected_format_currency,
        'application': {
            'name': 'android',
            'version': [3, 18, 0],
            'platform_version': [6, 0, 0],
        },
        'payment_options': ['card', 'coupon', 'corp'],
    }


@pytest.mark.parametrize(
    'coupons_code, expected_code',
    [(400, 500), (404, 500), (406, 406), (409, 409), (429, 429), (500, 500)],
)
def test_getreferral_via_coupons_http_code(
        coupons_code,
        expected_code,
        taxi_protocol,
        mockserver,
        getreferral_services,
):
    """
    Tests the correctness of http code in case of error inside coupons service.
    """

    @mockserver.handler('/coupons/v1/coupons/referral')
    def mock_coupons_getreferral(request):
        return mockserver.make_response('', coupons_code)

    response = taxi_protocol.post(
        '3.0/getreferral', json={'id': TEST_USER_ID}, bearer='test_token',
    )

    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'coupons_response',
    [
        [
            {
                'promocode': 'z0wg23h',
                'value': 300,
                'currency': 'RUB',
                'rides_count': 5,
                'rides_left': 3,
                'descr': 'Referral description',
                'message': 'Referral message',
            },
        ],
    ],
)
def test_getreferral_via_coupons_response_format(
        coupons_response, taxi_protocol, mockserver, getreferral_services,
):
    """
    Tests the format of proxied response.
    """

    @mockserver.json_handler('/coupons/v1/coupons/referral')
    def mock_coupons_getreferral(request):
        return coupons_response

    response = taxi_protocol.post(
        '3.0/getreferral', json={'id': TEST_USER_ID}, bearer='test_token',
    )

    response_json = response.json()

    assert response_json == coupons_response
