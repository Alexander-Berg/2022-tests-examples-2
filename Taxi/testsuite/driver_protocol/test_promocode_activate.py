import datetime

import pytest


@pytest.mark.parametrize(
    'params,json_body,exp_code,exp_response,exp_db',
    [
        (
            {
                'db': '16de978d526e40c0bf91e847245af744',
                'session': 'test_session_id_444FFFF',
            },
            {'code': '11111111'},
            400,
            {
                'error': {
                    'error_code': 'ERROR_PROMOCODE_NOT_FOUND',
                    'error_message': 'Promocode is not found.',
                },
            },
            None,
        ),
        (
            {
                'db': '16de978d526e40c0bf91e847245af741',
                'session': 'test_session_id_111FFFF',
            },
            {'code': '12344321'},
            400,
            {
                'error': {
                    'error_code': 'ERROR_PROMOCODE_HAS_PROMOCODE',
                    'error_message': 'You have active promocode.',
                },
            },
            None,
        ),
        (
            {
                'db': '16de978d526e40c0bf91e847245af743',
                'session': 'test_session_id_333FFFF',
            },
            {'code': '12344321'},
            400,
            {
                'error': {
                    'error_code': 'ERROR_PROMOCODE_HAS_WORKSHIFT',
                    'error_message': 'You have active workshift.',
                },
            },
            None,
        ),
        (
            {
                'db': '16de978d526e40c0bf91e847245af742',
                'session': 'test_session_id_222FFFF',
            },
            {'code': '12344321'},
            400,
            {
                'error': {
                    'error_code': 'ERROR_PROMOCODE_NOT_FOUND',
                    'error_message': 'Promocode is not found.',
                },
            },
            None,
        ),
        (
            {
                'db': '16de978d526e40c0bf91e847245af742',
                'session': 'test_session_id_222FFFF',
            },
            {'code': '12345678'},
            400,
            {
                'error': {
                    'error_code': 'ERROR_PROMOCODE_NOT_FOUND',
                    'error_message': 'Promocode is not found.',
                },
            },
            None,
        ),
        (
            {
                'db': '16de978d526e40c0bf91e847245af742',
                'session': 'test_session_id_222FFFF',
            },
            {'code': '87654321'},
            200,
            {'message': 'Duration 24. Min commission 0.1 byn.'},
            {
                '_id': 'promocode_id2',
                'clid': '999022',
                'code': '87654321',
                'finish': datetime.datetime(2018, 10, 11, 8, 30),
                'series_id': 'nominal2',
                'start': datetime.datetime(2018, 10, 10, 8, 30),
                'uuid': '2eaf04fe6dec4330a6f29a6a7701c452',
            },
        ),
        (
            {
                'db': '16de978d526e40c0bf91e847245af744',
                'session': 'test_session_id_444FFFF',
            },
            {'code': '00000000'},
            200,
            {'message': 'Duration 12. Min commission 1 rub.'},
            {
                '_id': 'promocode_id4',
                'clid': '999044',
                'code': '00000000',
                'finish': datetime.datetime(2018, 10, 10, 20, 30),
                'series_id': 'nominal1',
                'start': datetime.datetime(2018, 10, 10, 8, 30),
                'uuid': '2eaf04fe6dec4330a6f29a6a7701c454',
            },
        ),
        pytest.param(
            {
                'db': '16de978d526e40c0bf91e847245af744',
                'session': 'test_session_id_444FFFF',
            },
            {'code': '00000000'},
            403,
            None,
            None,
            marks=[
                pytest.mark.config(
                    DEPRECATED_PROMOCODES_COUNTRIES={
                        'enabled_countries': ['aze'],
                    },
                ),
            ],
        ),
    ],
    ids=[
        'promocode is not found',
        'has active promocode',
        'has active workshift',
        'promocode already activated',
        'promocode for another driver',
        'promocode for blr',
        'promocode for rus',
        'promocode for rus not allowed',
    ],
)
@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'driver_promocode.error.not_found': {'en': 'Promocode is not found.'},
        'driver_promocode.error.has_promocode': {
            'en': 'You have active promocode.',
        },
        'driver_promocode.error.has_workshift': {
            'en': 'You have active workshift.',
        },
        'driver_promocode.activated': {
            'en': 'Duration %(duration)s. Min commission %(commission)s.',
        },
    },
    tariff={
        'currency.rub': {'en': 'rub'},
        'currency.byn': {'en': 'byn'},
        'currency_with_sign.default': {'en': '$VALUE$ $SIGN$$CURRENCY$'},
    },
)
@pytest.mark.config(
    DRIVER_PROMOCODES_MIN_COMMISSION={'RUB': 1, 'BYN': 0.1, '__default__': 1},
    CURRENCY_ROUNDING_RULES={
        '__default__': {'10x': 10, '__default__': 1},
        'BYN': {'__default__': 1},
    },
    DEPRECATED_PROMOCODES_COUNTRIES={'enabled_countries': ['rus', 'blr']},
)
@pytest.mark.now('2018-10-10T11:30:00+0300')
def test_promocode_activate(
        taxi_driver_protocol,
        db,
        params,
        json_body,
        exp_code,
        exp_response,
        exp_db,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session(
        '16de978d526e40c0bf91e847245af741',
        'test_session_id_111FFFF',
        '2eaf04fe6dec4330a6f29a6a7701c451',
    )
    driver_authorizer_service.set_session(
        '16de978d526e40c0bf91e847245af742',
        'test_session_id_222FFFF',
        '2eaf04fe6dec4330a6f29a6a7701c452',
    )
    driver_authorizer_service.set_session(
        '16de978d526e40c0bf91e847245af743',
        'test_session_id_333FFFF',
        '2eaf04fe6dec4330a6f29a6a7701c453',
    )
    driver_authorizer_service.set_session(
        '16de978d526e40c0bf91e847245af744',
        'test_session_id_444FFFF',
        '2eaf04fe6dec4330a6f29a6a7701c454',
    )

    response = taxi_driver_protocol.post(
        '/driver/promocode/activate',
        params=params,
        json=json_body,
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == exp_code
    response_json = response.json()
    if exp_response:
        assert response_json == exp_response

    if response.status_code == 200:
        doc = db.driver_promocodes.find_one({'code': json_body['code']})
        doc.pop('updated')
        assert doc == exp_db
