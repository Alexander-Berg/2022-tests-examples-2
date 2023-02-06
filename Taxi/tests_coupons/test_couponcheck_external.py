import http

import pytest

from tests_coupons import util


def get_ok_grocery_coupons_response():
    return {
        'valid': True,
        'valid_any': True,
        'descriptions': [],
        'details': [],
    }


def mock_grocery_coupons(mockserver, valid, expected_request=None):
    response = get_ok_grocery_coupons_response()
    response['valid'] = valid

    @mockserver.json_handler('/grocery-coupons/internal/v1/coupons/validate')
    def _mock_grocery_coupons(request):
        assert 'X-Ya-Service-Ticket' in request.headers
        assert 'X-Request-Application' in request.headers
        if expected_request:
            assert request.json == expected_request
            if 'application' in expected_request:
                app_header = request.headers['X-Request-Application']
                assert app_header[app_header.find('app_ver=') :].startswith(
                    'app_ver='
                    + expected_request['application']['version'].join('.'),
                )
                assert app_header[app_header.find('app_name=') :].startswith(
                    'app_name=' + expected_request['application']['name'],
                )
                assert (
                    app_header[app_header.find('platform_ver2=') :].startswith(
                        'app_ver='
                        + expected_request['application']['platform_version'][
                            1
                        ],
                    )
                )
        return response

    return _mock_grocery_coupons


ORDER_ID = 'lavka:cart:12345'


def mock_request(code, service, locale='ru', yandex_uid='123', payload=None):
    request = {
        'code': code,
        'format_currency': True,
        'yandex_uids': [yandex_uid],
        'current_yandex_uid': yandex_uid,
        'phone_id': '5bbb5faf15870bd76635d5e2',
        'locale': locale,
        'user_ip': 'user_ip',
        'zone_name': 'moscow',
        'country': 'rus',
        'time_zone': 'Europe/Moscow',
        'payment_info': {'type': 'cash'},
        'application': {
            'name': 'iphone',
            'version': [4, 47, 0],
            'platform_version': [11, 1, 0],
        },
        'zone_classes': [
            {'class': 'econom', 'tanker_key': 'name.econom'},
            {'class': 'business', 'tanker_key': 'name.comfort'},
        ],
        'payment_options': ['card', 'coupon'],
        'selected_class': 'econom',
        'order_id': ORDER_ID,
        'service': service,
    }

    if payload is not None:
        request['payload'] = payload

    return request


EXPECTED_REQUESTS = {
    'taxi1': None,
    'serviceless1': None,
    'lavka1': {
        'coupon_id': 'lavka1',
        'series_id': 'unique_lavka',
        'external_ref': ORDER_ID,
        'series_meta': {
            'keyObj': {
                'keyArr': [1, 2, 3],
                'keyInnerObj': {'keyBool': True, 'keyNum': 321},
            },
            'keyStr': 'hello',
            'keyNull': None,
        },
    },
    'nulavka': {
        'coupon_id': 'nulavka',
        'series_id': 'nulavka',
        'external_ref': ORDER_ID,
    },
}


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(id='all_checks_are_async'),
        pytest.param(
            marks=pytest.mark.config(
                COUPONS_SYNC_CHECKS=['CheckExternalService'],
            ),
            id='external_checks_are_sync',
        ),
    ],
)
@pytest.mark.parametrize(
    'code, service, is_called, expected_request',
    [
        ('taxi1', None, False, EXPECTED_REQUESTS['taxi1']),
        ('taxi1', 'taxi', False, EXPECTED_REQUESTS['taxi1']),
        ('taxi1', 'grocery', False, None),
        ('serviceless1', None, False, EXPECTED_REQUESTS['serviceless1']),
        ('serviceless1', 'taxi', False, EXPECTED_REQUESTS['serviceless1']),
        ('taxi1', 'grocery', False, None),
        ('lavka1', 'grocery', True, EXPECTED_REQUESTS['lavka1']),
        ('lavka1', 'taxi', False, None),
        ('nulavka', 'grocery', True, EXPECTED_REQUESTS['nulavka']),
        ('nulavka', 'taxi', False, None),
    ],
)
async def test_external_service_call(
        taxi_coupons,
        local_services,
        mockserver,
        code,
        service,
        is_called,
        expected_request,
):
    local_services.add_card()
    request = mock_request(code, service, locale='en')
    grocery_coupons = mock_grocery_coupons(
        mockserver, True, expected_request=expected_request,
    )

    response = await taxi_coupons.post('v1/couponcheck', json=request)

    assert response.status_code == http.HTTPStatus.OK
    assert grocery_coupons.has_calls == is_called
    if expected_request:
        if 'series_meta' in expected_request:
            assert (
                response.json()['series_meta']
                == expected_request['series_meta']
            )
        else:
            assert 'series_meta' not in response.json()


LAVKA_SERVICE = 'grocery'


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.parametrize(
    'code, service, valid',
    [
        ('taxi1', None, True),
        ('taxi1', 'taxi', True),
        ('taxi1', 'grocery', False),
        ('serviceless1', None, True),
        ('serviceless1', 'taxi', True),
        ('serviceless1', 'grocery', False),
        pytest.param(
            'lavka1',
            None,
            False,
            marks=pytest.mark.xfail(
                reason='for now check is skipped for None service',
            ),
        ),
        ('lavka1', 'grocery', True),
        ('lavka1', 'taxi', False),
        pytest.param(
            'nulavka',
            None,
            False,
            marks=pytest.mark.xfail(
                reason='for now check is skipped if service is None',
            ),
        ),
        ('nulavka', 'grocery', True),
        ('nulavka', 'eda', False),
    ],
)
async def test_external_service_mismatch(
        taxi_coupons, local_services, mockserver, code, service, valid,
):
    local_services.add_card()
    request = mock_request(code, service, locale='en')
    mock_grocery_coupons(mockserver, True)

    response = await taxi_coupons.post('v1/couponcheck', json=request)

    assert response.status_code == http.HTTPStatus.OK
    data = response.json()
    assert data['valid'] == valid


@pytest.mark.parametrize('code', ['lavka1', 'nulavka'])
async def test_external_service_400(
        taxi_coupons, local_services, mockserver, code,
):
    local_services.add_card()
    request = mock_request(code, 'lavka', locale='en')

    @mockserver.json_handler('/grocery-coupons/internal/v1/coupons/validate')
    def _mock_grocery_coupons(request):
        return mockserver.make_response(
            '{"code": "BAD_REQUEST", "message": "Bad Request"}',
            status=http.HTTPStatus.BAD_REQUEST,
            content_type='application/json',
            charset='utf-8',
        )

    response = await taxi_coupons.post('v1/couponcheck', json=request)

    assert response.status_code == http.HTTPStatus.OK
    data = response.json()
    assert not data['valid']


LAVKA_SERVICE = 'grocery'


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.parametrize(
    'code, external_valid',
    [
        ('lavka1', True),
        ('lavka1', False),
        ('nulavka', True),
        ('nulavka', False),
    ],
)
async def test_external_service(
        taxi_coupons, local_services, mockserver, code, external_valid,
):
    local_services.add_card()
    request = mock_request(code, LAVKA_SERVICE, locale='en')
    grocery_coupons = mock_grocery_coupons(mockserver, external_valid)

    response = await taxi_coupons.post('v1/couponcheck', json=request)

    assert response.status_code == http.HTTPStatus.OK
    data = response.json()
    assert data['valid'] == external_valid
    assert grocery_coupons.has_calls


@pytest.mark.parametrize('code', [pytest.param('lavka777')])
@pytest.mark.config(COUPONS_LAVKA_PREFIXES=['lavka'])
async def test_lavka_err_response(taxi_coupons, code, local_services):
    request = mock_request(code, LAVKA_SERVICE, locale='en')
    response = await taxi_coupons.post('v1/couponcheck', json=request)

    assert response.status_code == http.HTTPStatus.OK

    resp = response.json()
    assert resp['error_code'] == util.ServiceErrors.ERROR_LAVKA_PROMOCODE.value
    assert resp['details'] == ['Invalid lavka code']


@pytest.mark.config(COUPONS_EXTERNAL_VALIDATION_SERIES={'maas3': 'maas'})
@pytest.mark.parametrize(
    (
        'code, request_payload, expected_maas_request, maas_response, '
        'maas_status_code, expected_valid, expected_error_code'
    ),
    [
        pytest.param(
            'maas31',
            {'waypoints': [[37.5, 55.5], [37.6, 55.6]]},
            {
                'coupon_id': 'maas31',
                'series_id': 'maas3',
                'external_ref': ORDER_ID,
                'payload': {'waypoints': [[37.5, 55.5], [37.6, 55.6]]},
            },
            {'valid': True},
            200,
            True,
            None,
            id='maas_valid',
        ),
        pytest.param(
            'maas31',
            {'waypoints': [[37.5, 55.5]]},
            {
                'coupon_id': 'maas31',
                'series_id': 'maas3',
                'external_ref': ORDER_ID,
                'payload': {'waypoints': [[37.5, 55.5]]},
            },
            {'valid': False, 'error_code': 'route_without_point_b'},
            200,
            False,
            'ERROR_EXTERNAL_VALIDATION_FAILED',
            id='maas_not_valid',
        ),
        pytest.param(
            'maas31',
            {'waypoints': [[37.5, 55.5], [37.6, 55.6]]},
            {
                'coupon_id': 'maas31',
                'series_id': 'maas3',
                'external_ref': ORDER_ID,
                'payload': {'waypoints': [[37.5, 55.5], [37.6, 55.6]]},
            },
            {},
            500,
            True,
            None,
            marks=pytest.mark.config(
                COUPONS_EXTERNAL_VALIDATORS_SETTINGS={
                    'settings': {
                        'maas': {'ignore_errors': True},
                        '__default__': {'ignore_errors': False},
                    },
                },
            ),
            id='maas_ignore_error_coupon_valid',
        ),
        pytest.param(
            'maas31',
            {'waypoints': [[37.5, 55.5], [37.6, 55.6]]},
            {
                'coupon_id': 'maas31',
                'series_id': 'maas3',
                'external_ref': ORDER_ID,
                'payload': {'waypoints': [[37.5, 55.5], [37.6, 55.6]]},
            },
            {},
            500,
            False,
            'ERROR_EXTERNAL_SERVICE_UNAVAILABLE',
            id='maas_do_not_ignore_error_coupon_not_valid',
        ),
        pytest.param(
            'taxi1', None, None, {}, 500, True, None, id='not_maas_coupon',
        ),
    ],
)
async def test_maas_external_check(
        taxi_coupons,
        local_services,
        mockserver,
        code,
        request_payload,
        expected_maas_request,
        maas_response,
        maas_status_code,
        expected_valid,
        expected_error_code,
):
    local_services.add_card()

    request = mock_request(code, 'taxi', locale='ru', payload=request_payload)

    @mockserver.json_handler('/maas/internal/maas/v1/validate-maas-coupon')
    def _mock_maas(maas_request):
        assert maas_request.headers['X-YaTaxi-PhoneId'] == request['phone_id']
        assert (
            maas_request.headers['X-Yandex-UID']
            == request['current_yandex_uid']
        )
        assert maas_request.json == expected_maas_request
        return mockserver.make_response(
            json=maas_response, status=maas_status_code,
        )

    response = await taxi_coupons.post(
        'v1/couponcheck',
        json=request,
        headers={'X-YaTaxi-PhoneId': 'phone_id', 'X-Yandex-UID': 'uid'},
    )

    if expected_maas_request is not None:
        assert _mock_maas.times_called > 0
    else:
        assert _mock_maas.times_called == 0

    assert response.status_code == http.HTTPStatus.OK

    response_json = response.json()

    assert response_json['valid'] == expected_valid
    assert response_json.get('error_code') == expected_error_code


@pytest.mark.config(
    COUPONS_EXTERNAL_VALIDATION_SERVICES=['eats'],
    UAFS_COUPONS_FETCH_GLUE=True,
    UAFS_COUPONS_PASS_GLUE_TO_EATS_COUPONS=True,
)
@pytest.mark.parametrize(
    'code, expected_error_code, expected_details',
    [
        pytest.param(
            'eats123',
            'SOME_EATS_ERROR_CODE',
            None,
            marks=pytest.mark.config(
                COUPONS_EXTERNAL_SERVICES_FORWARD_ERRORS={
                    'forward_codes_for_services': ['eats'],
                    'forward_description_for_services': [],
                },
            ),
        ),
        pytest.param(
            'eats123',
            None,
            'Some eats error description',
            marks=pytest.mark.config(
                COUPONS_EXTERNAL_SERVICES_FORWARD_ERRORS={
                    'forward_codes_for_services': [],
                    'forward_description_for_services': ['eats'],
                },
            ),
        ),
        pytest.param(
            'eats123',
            'SOME_EATS_ERROR_CODE',
            'Some eats error description',
            marks=pytest.mark.config(
                COUPONS_EXTERNAL_SERVICES_FORWARD_ERRORS={
                    'forward_codes_for_services': ['eats'],
                    'forward_description_for_services': ['eats'],
                },
            ),
        ),
    ],
)
async def test_error_codes_forwarding(
        taxi_coupons,
        mockserver,
        code,
        local_services,
        expected_error_code,
        expected_details,
):
    @mockserver.json_handler('/eats-coupons/internal/v1/coupons/validate')
    def _mock_eats_coupons_validate(req):
        assert req.json['series_id'] is not None
        assert req.json['glue'] == ['eats_uid1', 'eats_uid2', 'eats_uid3']
        assert req.json['source_handler'] == 'check'
        return {
            'valid': False,
            'valid_any': False,
            'descriptions': [],
            'details': [],
            'error_code': 'SOME_EATS_ERROR_CODE',
            'error_description': 'Some eats error description',
        }

    @mockserver.json_handler('/uantifraud/v1/glue')
    def _mock_uafs(req):
        assert req.json == {'sources': ['taxi', 'eats'], 'passport_uid': '123'}
        return {
            'sources': {
                'taxi': {'passport_uids': ['taxi_uid1', 'taxi_uid2']},
                'eats': {
                    'passport_uids': ['eats_uid1', 'eats_uid2', 'eats_uid3'],
                },
            },
        }

    eats_coupons_mock = _mock_eats_coupons_validate

    local_services.add_card()

    request = mock_request(code, 'eats')
    request['payload'] = {'brand_ids': 'brand1'}
    response = await taxi_coupons.post('v1/couponcheck', json=request)

    assert eats_coupons_mock.has_calls
    assert response.status_code == 200

    data = response.json()

    if expected_error_code:
        assert data['error_code'] == expected_error_code
    else:
        assert data['error_code'] == 'ERROR_EXTERNAL_VALIDATION_FAILED'

    if expected_details:
        assert data['details'] == [expected_details]
    else:
        assert data['details'] == ['Invalid code']

    assert data['descr'] == 'Wrong code'

    assert await _mock_uafs.wait_call()
