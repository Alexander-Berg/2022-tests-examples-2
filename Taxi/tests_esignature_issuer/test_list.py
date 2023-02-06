import pytest

SIGNATURE1 = {
    'signature_id': 'signature_id1',
    'doc_id': 'doc_id1',
    'doc_type': 'cargo',
    'signer_id': 'signer_id1',
    'properties': {
        'sign_type': 'confirmation_code',
        'send_properties': [{'send_type': 'ucommunications_sms'}],
    },
    'signer_type': 'sender',
    'idempotency_token': '1',
}

SIGNATURE2 = {
    'signature_id': 'signature_id2',
    'doc_id': 'doc_id1',
    'doc_type': 'cargo',
    'signer_id': 'signer_id1',
    'properties': {'sign_type': 'ya_sms'},
    'signer_type': 'sender',
    'idempotency_token': '2',
}

SIGNATURE3 = {
    'signature_id': 'signature_id3',
    'doc_id': 'doc_id1',
    'doc_type': 'cargo',
    'signer_id': 'signer_id1',
    'properties': {'sign_type': 'ucommunications_sms'},
    'signer_type': 'sender',
    'idempotency_token': '2',
}


@pytest.mark.usefixtures('mock_ucommunications')
async def test_list(
        taxi_esignature_issuer, create_signature, confirm_signature,
):
    create_signature(**SIGNATURE1)
    confirm_signature(
        SIGNATURE1['signature_id'],
        SIGNATURE1['doc_type'],
        SIGNATURE1['doc_id'],
    )
    create_signature(**SIGNATURE2)
    create_signature(**SIGNATURE3)
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/list', json={'doc_type': 'cargo', 'doc_id': 'doc_id1'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['signatures'][0].pop('signed_at')
    code_masked = response_json['signatures'][0].pop('code_masked')
    assert len(code_masked) == 6
    assert code_masked[2:4] == '**'
    assert response_json == {
        'doc_type': 'cargo',
        'doc_id': 'doc_id1',
        'signatures': [
            {
                'signature_id': 'signature_id1',
                'signer_id': 'signer_id1',
                'sign_type': 'confirmation_code',
            },
            {
                'signature_id': 'signature_id2',
                'signer_id': 'signer_id1',
                'sign_type': 'ya_sms',
            },
            {
                'signature_id': 'signature_id3',
                'signer_id': 'signer_id1',
                'sign_type': 'ucommunications_sms',
            },
        ],
    }
