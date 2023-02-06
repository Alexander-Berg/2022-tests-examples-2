import pytest

REQUEST_1 = {
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

REQUEST_2 = {
    'signature_id': 'signature_id2',
    'doc_id': 'doc_id1',
    'doc_type': 'cargo',
    'signer_id': 'signer_id2',
    'properties': {
        'sign_type': 'confirmation_code',
        'send_properties': [{'send_type': 'ucommunications_sms'}],
    },
    'signer_type': 'sender',
    'idempotency_token': '2',
}


@pytest.mark.parametrize(
    'create_request',
    [
        pytest.param([REQUEST_1], id='one signature'),
        pytest.param([REQUEST_1, REQUEST_2], id='two signatures'),
    ],
)
async def test_create(
        taxi_esignature_issuer, get_req_headers, create_request, pgsql,
):
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/bulk-create',
        json=create_request,
        headers=get_req_headers(),
    )
    assert response.status_code == 200

    with pgsql['esignature_issuer'].cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM esignature_issuer.signatures')
        signatures_cnt = cursor.fetchone()[0]
        cursor.execute(
            'SELECT COUNT(*) FROM esignature_issuer.verification_codes',
        )
        codes_cnt = cursor.fetchone()[0]

        assert signatures_cnt == len(create_request)
        assert codes_cnt == len(create_request)

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/bulk-create',
        json=create_request,
        headers=get_req_headers(),
    )
    assert response.status_code == 200

    with pgsql['esignature_issuer'].cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM esignature_issuer.signatures')
        assert signatures_cnt == cursor.fetchone()[0]
        cursor.execute(
            'SELECT COUNT(*) FROM esignature_issuer.verification_codes',
        )
        assert codes_cnt == cursor.fetchone()[0]


async def test_send(
        taxi_esignature_issuer,
        testpoint,
        get_req_headers,
        mock_ucommunications,
):
    @testpoint('test_retry_in_create_handler')
    def point1(data):
        pass

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/bulk-create',
        json=[REQUEST_1, REQUEST_2],
        headers=get_req_headers(),
    )
    assert response.status_code == 200

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=REQUEST_1, headers=get_req_headers(),
    )
    assert response.status_code == 200

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=REQUEST_1, headers=get_req_headers(),
    )
    assert point1.has_calls
    assert response.status_code == 200
