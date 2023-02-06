import pytest


def _get_valid_signature():
    return (
        'AAAAAAAAAAAAAAAAIPCxW/hFW68BYl3XZLbaNf0UYDy9'
        'b1cGpWJSRlPPY69LbmKeWz2LoYH0aTDlJoWqsjiywA'
    )


def get_wrong_signature():
    return (
        'AAAAAAAAAAAAAAAAIPCxW/hFW68BYl3XZLbaNf0UYDy9'
        'b1cGpWJSRlPPY69LbmKeWz2LoYH0aTDlJoWqsjiy6g'
    )


def _get_valid_signature_with_wrong_hash():
    return (
        'AAAAAAAAAAAAAAAAIPCxWzesubAU6Eucd0qlKaELkli'
        '8b1cGpWJSRlPPY69LbmKeWz2LoYH0aTDlJoWqsjiywA'
    )


def _get_valid_request(
        licenses=None, driver_id=None, signature=None, missing=None,
):
    _REQUEST = {
        'licenses': ['license1'] if licenses is None else licenses,
        'driver_id': 'driver_id1' if driver_id is None else driver_id,
        'application': 'some_app',
        'signature': (
            _get_valid_signature() if signature is None else signature
        ),
    }
    return {
        k: v
        for k, v in _REQUEST.items()
        if missing is None or k not in missing
    }


def _check_db(db, licenses, frauder, fraud_reason):
    records = db.antifraud_driver_client_info.find(
        {'license': {'$in': licenses}},
    )
    records_by_license = {record['license']: record for record in records}

    for license in licenses:
        record = records_by_license[license]
        assert 'created' in record
        assert 'updated' in record
        assert record['license'] == license
        assert record['frauder'] == frauder
        assert record['fraud_reason'] == fraud_reason


def _check_base(
        taxi_antifraud, signature, frauder, fraud_reason, db, testpoint,
):
    @testpoint('on_exception')
    def on_exception(_):
        assert False

    input = _get_valid_request(signature=signature)

    response = taxi_antifraud.post('v1/client/driver/signature/check', input)
    assert response.status_code == 200
    assert not response.json()

    assert not on_exception.has_calls

    _check_db(db, input['licenses'], frauder, fraud_reason)


@pytest.mark.parametrize(
    'signature,frauder,fraud_reason,enabled',
    [
        # happy path (good hash, config on) -> no fraud
        #
        # key: sha256('DEADBEEF' + 'license1')
        # iv: bytearray('0' * 12)
        # ts: 1538388000
        # hash: bytearray('0' * 32)
        (_get_valid_signature(), False, 'no_fraud', True),
        # happy path (bad hash, config on) -> fraud
        #
        # key: sha256('DEADBEEF' + 'license1')
        # iv: bytearray('0' * 12)
        # ts: 1538388000
        # hash: bytearray('1' + '0' * 31)
        (_get_valid_signature_with_wrong_hash(), True, 'bad_signature', True),
        # happy path (bad hash, config off) -> no fraud
        #
        # key: sha256('DEADBEEF' + 'license1')
        # iv: bytearray('0' * 12)
        # ts: 1538388000
        # hash: bytearray('1' + '0' * 31)
        (_get_valid_signature_with_wrong_hash(), False, 'no_fraud', False),
    ],
)
@pytest.mark.now('2018-10-01T10:00:00+0000')
def test_check_base(
        taxi_antifraud,
        signature,
        frauder,
        fraud_reason,
        enabled,
        db,
        testpoint,
        config,
):
    config.set_values(
        dict(AFS_CLIENT_DRIVER_IOS_SIMPLE_SIGNATURE_CHECK=enabled),
    )
    _check_base(
        taxi_antifraud, signature, frauder, fraud_reason, db, testpoint,
    )


@pytest.mark.parametrize('enabled', [True, False])
@pytest.mark.parametrize(
    'input,error_message',
    [
        (_get_valid_request(missing=['licenses']), 'no licenses'),
        (_get_valid_request(missing=['driver_id']), 'no driver_id'),
        (
            _get_valid_request(missing=['signature']),
            'field signature is missing',
        ),
        (_get_valid_request(licenses=[]), 'licenses or driver_id is empty'),
        (_get_valid_request(driver_id=''), 'licenses or driver_id is empty'),
        (
            _get_valid_request(signature=_get_valid_signature()[:-1]),
            'attempt to decode a value not in base64 char set',
        ),
        (
            _get_valid_request(signature=_get_valid_signature()[:-2]),
            'wrong message size: 63',
        ),
        (
            _get_valid_request(signature=get_wrong_signature()),
            'HashVerificationFilter: message hash or MAC not valid',
        ),
    ],
)
@pytest.mark.now('2018-10-01T10:00:00+0000')
def test_check_wrong_input(
        taxi_antifraud, enabled, input, error_message, db, testpoint, config,
):
    config.set_values(
        dict(AFS_CLIENT_DRIVER_IOS_SIMPLE_SIGNATURE_FAIL_CHECK=enabled),
    )

    @testpoint('on_exception')
    def on_exception(data):
        assert error_message == data['error_message']

    response = taxi_antifraud.post('v1/client/driver/signature/check', input)
    assert response.status_code == 200
    assert not response.json()

    on_exception.wait_call()

    if input.get('licenses') and input.get('driver_id'):
        _check_db(
            db,
            input['licenses'],
            **{
                'frauder': enabled,
                'fraud_reason': 'bad_signature' if enabled else 'no_fraud',
            },
        )
