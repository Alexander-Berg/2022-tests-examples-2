import uuid

import pytest


@pytest.mark.usefixtures('mock_ucommunications')
async def test_passport_ucommunications(
        taxi_esignature_issuer,
        create_signature,
        get_signature,
        get_req_headers,
):
    passport_signature = create_signature(properties={'sign_type': 'ya_sms'})

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create',
        json={
            **passport_signature,
            'properties': {
                'sign_type': 'confirmation_code',
                'send_properties': [{'send_type': 'ucommunications_sms'}],
            },
            'idempotency_token': str(uuid.uuid4()),
        },
        headers=get_req_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {}

    ucommunications_signature = get_signature(
        signature_id=passport_signature['signature_id'],
        doc_type=passport_signature['doc_type'],
        doc_id=passport_signature['doc_id'],
    )
    assert 'code' not in passport_signature
    assert 'code' in ucommunications_signature
    assert (
        passport_signature['validation_id']
        != ucommunications_signature['validation_id']
    )
    ucommunications_signature.pop('sms_last_sent_at')

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/confirm',
        json={**passport_signature, 'code': '0000'},
        headers=get_req_headers(),
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'invalid_code'

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/confirm',
        json={**ucommunications_signature},
        headers=get_req_headers(),
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
