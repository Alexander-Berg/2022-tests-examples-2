SIGNATURE = {
    'signature_id': 'signature_id1',
    'doc_id': 'doc_id1',
    'doc_type': 'cargo',
    'signer_id': 'signer_id1',
    'signer_type': 'sender',
    'properties': {'sign_type': 'ya_sms'},
    'idempotency_token': '1',
}

CONFIRM_REQ_BODY = {
    'signature_id': 'signature_id1',
    'doc_type': 'cargo',
    'doc_id': 'doc_id1',
    'code': '0000',
}


async def test_create_disabled(taxi_esignature_issuer, get_req_headers):
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=SIGNATURE, headers=get_req_headers(),
    )
    assert response.status_code == 400


async def test_confirm_disabled(
        taxi_esignature_issuer, get_req_headers, create_signature,
):
    create_signature(**SIGNATURE)

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/confirm',
        json=CONFIRM_REQ_BODY,
        headers=get_req_headers(),
    )
    assert response.status_code == 400
