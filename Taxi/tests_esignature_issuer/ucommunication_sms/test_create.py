import datetime
import uuid

import pytest
import pytz


@pytest.mark.parametrize(
    ('intent', 'tanker_key', 'extra_data'),
    (
        (None, None, None),
        ('cargo_verification', None, None),
        ('cargo_verification', 'some_tanker_key', {'key': 'value'}),
        ('cargo_verification', 'some_tanker_key', {}),
    ),
)
async def test_success(
        taxi_esignature_issuer,
        mock_ucommunications,
        get_signature,
        get_req_headers,
        intent,
        tanker_key,
        extra_data,
):
    request_json = {
        'signature_id': 'cb2a2ef57f2842b99df08eacc3a9fedf',
        'doc_id': '02e03cfa3b66436ca90e9aabd5e22ea6',
        'doc_type': 'cargo_claims',
        'signer_id': '67214c13ba71400e9b2a78c520c9e186',
        'signer_type': 'sender_to_driver',
        'properties': {
            'sign_type': 'confirmation_code',
            'send_properties': [{'send_type': 'ucommunications_sms'}],
        },
        'idempotency_token': '052b764c-24f9-4f76-a586-2fdf64fbc49d',
    }

    if intent:
        send_props = request_json['properties']['send_properties']
        for send_prop in send_props:
            if send_prop['send_type'] == 'ucommunications_sms':
                send_prop['intent'] = intent
                if tanker_key:
                    send_prop['tanker_key'] = tanker_key
                send_prop['extra_data'] = extra_data

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=request_json, headers=get_req_headers(),
    )
    if extra_data == {}:
        assert response.status_code == 400
        assert response.json() == {
            'code': 'empty_extra_data',
            'message': 'extra_data is empty',
        }
        return
    assert response.status_code == 200
    assert response.json() == {}

    assert mock_ucommunications.times_called == 1
    result = await mock_ucommunications.wait_call()

    verification_code = result['request'].json['text']['params']['code']
    assert len(verification_code) == 6
    assert verification_code.isdigit()
    result['request'].json['text']['params'].pop('code')
    assert result['request'].json == {
        'phone_id': request_json['signer_id'],
        'text': {
            'keyset': 'notify',
            'key': tanker_key or 'cargo_verification_code',
            'params': extra_data or {},
        },
        'locale': 'en',
        'intent': intent or 'cargo_default',
    }

    signature = get_signature(
        signature_id=request_json['signature_id'],
        doc_type=request_json['doc_type'],
        doc_id=request_json['doc_id'],
    )
    assert signature['code'] == verification_code
    assert 'validation_id' in signature


async def test_double_request(
        taxi_esignature_issuer, get_req_headers, create_signature,
):
    signature = create_signature()

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json={**signature}, headers=get_req_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {}


async def test_same_code(
        taxi_esignature_issuer,
        mock_ucommunications,
        create_signature,
        get_signature,
        get_req_headers,
):
    signature = create_signature()

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create',
        json={**signature, 'idempotency_token': str(uuid.uuid4())},
        headers=get_req_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {}

    assert mock_ucommunications.times_called == 1
    result = await mock_ucommunications.wait_call()
    second_code = result['request'].json['text']['params']['code']
    assert signature['code'] == second_code

    second_signature = get_signature(
        signature_id=signature['signature_id'],
        doc_type=signature['doc_type'],
        doc_id=signature['doc_id'],
    )
    assert signature['code'] == second_signature['code']


async def test_check_already_confirmed(
        taxi_esignature_issuer,
        create_signature,
        confirm_signature,
        get_req_headers,
):
    signature = create_signature()
    confirm_signature(
        signature_id=signature['signature_id'],
        doc_type=signature['doc_type'],
        doc_id=signature['doc_id'],
    )

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create',
        json={**signature, 'idempotency_token': str(uuid.uuid4())},
        headers=get_req_headers(),
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'already_confirmed',
        'message': 'sign is already confirmed',
    }


async def test_delay(
        taxi_esignature_issuer, create_signature, get_req_headers,
):
    signature = create_signature(
        sms_last_sent_at=datetime.datetime.utcnow().replace(tzinfo=pytz.UTC),
    )

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create',
        json={**signature, 'idempotency_token': str(uuid.uuid4())},
        headers=get_req_headers(),
    )
    assert response.status_code == 429
    assert response.json() == {
        'code': 'too_many_requests',
        'message': 'wait a few seconds to retry',
    }


async def test_signature_limit(
        taxi_esignature_issuer, create_signature, get_req_headers,
):
    signature = create_signature(sms_per_signature_count=5)

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create',
        json={**signature, 'idempotency_token': str(uuid.uuid4())},
        headers=get_req_headers(),
    )
    assert response.status_code == 429
    assert response.json() == {
        'code': 'too_many_requests',
        'message': 'too many messages sent for this signature',
    }


async def test_signer_limit(
        taxi_esignature_issuer, create_signature, get_req_headers,
):
    signature = create_signature(sms_today_count=50)

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create',
        json={**signature, 'idempotency_token': str(uuid.uuid4())},
        headers=get_req_headers(),
    )
    assert response.status_code == 429
    assert response.json() == {
        'code': 'too_many_requests',
        'message': 'too many messages sent this day',
    }


async def test_signer_id_not_changed(
        taxi_esignature_issuer, create_signature, get_req_headers,
):
    signature = create_signature()

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create',
        json={
            **signature,
            'signer_id': str(uuid.uuid4()).replace('', '-'),
            'idempotency_token': str(uuid.uuid4()),
        },
        headers=get_req_headers(),
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'bad_signer_id',
        'message': 'trying to create signature with another signer_id ',
    }


async def test_signer_type_not_changed(
        taxi_esignature_issuer, create_signature, get_req_headers,
):
    signature = create_signature()

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create',
        json={
            **signature,
            'signer_type': 'cargo_misc',
            'idempotency_token': str(uuid.uuid4()),
        },
        headers=get_req_headers(),
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'bad_signer_type',
        'message': 'trying to create signature with another signer_type ',
    }
