import datetime

import pytest


def test_simple(taxi_protocol, db):
    db.trust_verifications.update(
        {'binding_id': 'binding_id1'},
        {
            'uid': '4003514353',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'verification_id': '5cbf6b957c4448ac8964f0fcf3dbff78',
            'method': 'auto',
            'status': 'in_progress',
            'start_ts': datetime.datetime(2018, 2, 7, 22, 33, 9),
        },
        upsert=True,
    )

    response = taxi_protocol.post(
        '3.0/paymentverifications',
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'verification_id': '5cbf6b957c4448ac8964f0fcf3dbff78',
            'force_cache_invalidate': False,
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


def test_sort(taxi_protocol, db):
    db.trust_verifications.update(
        {
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'verification_id': '5cbf6b957c4448ac8964f0fcf3dbff79',
        },
        {
            'uid': '4003514353',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'verification_id': '5cbf6b957c4448ac8964f0fcf3dbff79',
            'method': 'auto',
            'status': '3ds_required',
            'finish_binding_url': 'https://ya.ru',
            '3ds_url': 'https://ya.ru',
            'start_ts': datetime.datetime(2018, 2, 7, 22, 39, 9),
        },
        upsert=True,
    )

    db.trust_verifications.update(
        {
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'verification_id': '5cbf6b957c4448ac8964f0fcf3dbff78',
        },
        {
            'uid': '4003514353',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'verification_id': '5cbf6b957c4448ac8964f0fcf3dbff78',
            'method': 'auto',
            'status': 'in_progress',
            'start_ts': datetime.datetime(2018, 2, 7, 22, 33, 9),
        },
        upsert=True,
    )

    response = taxi_protocol.post(
        '3.0/paymentverifications',
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'force_cache_invalidate': False,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
        'verification': {
            'id': '5cbf6b957c4448ac8964f0fcf3dbff79',
            'method': 'auto',
            'status': '3ds_required',
            'finish_binding_url': 'https://ya.ru',
            '3ds_url': 'https://ya.ru',
        },
    }


def test_404(taxi_protocol, db, mockserver):
    response = taxi_protocol.post(
        '3.0/paymentverifications',
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'verification_id': '5cbf6b957c4448ac8964f0fcf3dbff78',
            'force_cache_invalidate': False,
        },
    )

    assert response.status_code == 404


def test_request_verification_update(taxi_protocol, db, mockserver):
    @mockserver.json_handler(
        '/trust-bindings/bindings/6cbf6b957c4448ac8964f'
        '0fcf3dbff78/verifications/5cbf6b957c4448ac8964'
        'f0fcf3dbff78/',
    )
    def mock_trust(request):
        return {
            'uid': '4003514353',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'verification': {
                'id': '5cbf6b957c4448ac8964f0fcf3dbff78',
                'method': 'auto',
                'status': '3ds_required',
                'start_ts': '2018-02-07T22:33:09.582Z',
            },
        }

    response = taxi_protocol.post(
        '3.0/paymentverifications',
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'verification_id': '5cbf6b957c4448ac8964f0fcf3dbff78',
            'force_cache_invalidate': True,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
        'verification': {
            'id': '5cbf6b957c4448ac8964f0fcf3dbff78',
            'method': 'auto',
            'status': '3ds_required',
        },
    }

    obj = db.trust_verifications.find_one()
    obj.pop('_id')
    assert obj == {
        'uid': '4003514353',
        'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
        'verification_id': '5cbf6b957c4448ac8964f0fcf3dbff78',
        'method': 'auto',
        'status': '3ds_required',
        'start_ts': datetime.datetime(2018, 2, 7, 22, 33, 9, 582000),
    }


def test_request_binding_update(taxi_protocol, db, mockserver):
    @mockserver.json_handler(
        '/trust-bindings/bindings/' '6cbf6b957c4448ac8964f0fcf3dbff78/verify/',
    )
    def mock_trust(request):
        return {
            'uid': '4003514353',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'verification': {
                'id': '5cbf6b957c4448ac8964f0fcf3dbff78',
                'method': 'auto',
                'status': 'in_progress',
                'start_ts': '2018-02-07T22:33:09.582Z',
            },
        }

    response = taxi_protocol.post(
        '3.0/paymentverifications',
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

    obj = db.trust_verifications.find_one()
    obj.pop('_id')
    assert obj == {
        'uid': '4003514353',
        'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
        'verification_id': '5cbf6b957c4448ac8964f0fcf3dbff78',
        'method': 'auto',
        'status': 'in_progress',
        'start_ts': datetime.datetime(2018, 2, 7, 22, 33, 9, 582000),
    }


@pytest.mark.config(
    CARD_BINDING_TRUST_ERROR_CODE_TO_TRANSLATION_ERROR_CODE_MAP={
        '__default__': 'card_binding_error_message.default',
        'declined_by_issuer': 'card_binding_error_message.refer_your_bank',
    },
)
@pytest.mark.translations(
    client_messages={
        'card_binding_error_message.default': {'ru': 'default error message'},
        'card_binding_error_message.refer_your_bank': {
            'ru': 'refer to your bank',
        },
    },
)
@pytest.mark.parametrize(
    'authorize_rc, error_message',
    [
        (None, 'default error message'),
        ('declined_by_issuer', 'refer to your bank'),
    ],
)
def test_request_error_message(
        taxi_protocol, mockserver, authorize_rc, error_message,
):
    @mockserver.json_handler(
        '/trust-bindings/bindings/' '6cbf6b957c4448ac8964f0fcf3dbff78/verify/',
    )
    def mock_trust(request):
        response = {
            'uid': '4003514353',
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

    response = taxi_protocol.post(
        '3.0/paymentverifications',
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
            'status': 'failure',
            'error_message': error_message,
        },
    }


def test_request_binding_404(taxi_protocol, db, mockserver):
    @mockserver.json_handler(
        '/trust-bindings/bindings/' '6cbf6b957c4448ac8964f0fcf3dbff78/verify/',
    )
    def mock_trust(request):
        return mockserver.make_response('', 404)

    response = taxi_protocol.post(
        '3.0/paymentverifications',
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'force_cache_invalidate': True,
        },
    )

    assert response.status_code == 404


def test_request_binding_429(taxi_protocol, db, mockserver):
    @mockserver.json_handler(
        '/trust-bindings/bindings/' '6cbf6b957c4448ac8964f0fcf3dbff78/verify/',
    )
    def mock_trust(request):
        return mockserver.make_response(
            '',
            429,
            headers={'Date': '2018-02-07T22:34:09.582Z', 'Retry-After': 1234},
        )

    response = taxi_protocol.post(
        '3.0/paymentverifications',
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'force_cache_invalidate': True,
        },
    )
    assert response.headers['Retry-After'] == '1234'

    assert response.status_code == 429


def test_request_binding_422(taxi_protocol, db, mockserver):
    @mockserver.json_handler(
        '/trust-bindings/bindings/' '6cbf6b957c4448ac8964f0fcf3dbff78/verify/',
    )
    def mock_trust(request):
        return mockserver.make_response('', 422)

    response = taxi_protocol.post(
        '3.0/paymentverifications',
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'binding_id': '6cbf6b957c4448ac8964f0fcf3dbff78',
            'force_cache_invalidate': True,
        },
    )
    assert response.status_code == 422
