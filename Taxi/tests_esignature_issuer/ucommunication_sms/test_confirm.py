import uuid


async def test_valid_code(
        taxi_esignature_issuer,
        create_signature,
        get_signature,
        get_req_headers,
):
    signature = create_signature()

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/confirm',
        json={**signature},
        headers=get_req_headers(),
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

    new_state = get_signature(
        signature_id=signature['signature_id'],
        doc_type=signature['doc_type'],
        doc_id=signature['doc_id'],
    )
    assert new_state['signed_at']


async def test_invalid_code(
        taxi_esignature_issuer,
        create_signature,
        get_signature,
        get_req_headers,
):
    signature = create_signature()

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/confirm',
        json={**signature, 'code': '000000'},
        headers=get_req_headers(),
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'invalid_code'

    new_state = get_signature(
        signature_id=signature['signature_id'],
        doc_type=signature['doc_type'],
        doc_id=signature['doc_id'],
    )
    assert 'signed_at' not in new_state
    assert signature['code'] == new_state['code']


async def test_not_found(taxi_esignature_issuer, get_req_headers):
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/confirm',
        json={
            'signature_id': str(uuid.uuid4()).replace('-', ''),
            'doc_type': 'cargo_claims',
            'doc_id': str(uuid.uuid4()).replace('-', ''),
            'signer_type': 'sender_to_driver',
            'code': '000000',
        },
        headers=get_req_headers(),
    )
    assert response.status_code == 404


async def test_code_change(
        taxi_esignature_issuer,
        create_signature,
        get_signature,
        get_req_headers,
):
    signature = create_signature(check_count=5)

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/confirm',
        json={**signature, 'code': '000000'},
        headers=get_req_headers(),
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'invalid_code'

    new_state = get_signature(
        signature_id=signature['signature_id'],
        doc_type=signature['doc_type'],
        doc_id=signature['doc_id'],
    )
    assert 'signed_at' not in new_state
    assert signature['code'] != new_state['code']
