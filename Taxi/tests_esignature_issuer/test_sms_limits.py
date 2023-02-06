REQ_BODY = {
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

REQ_BODY_2 = {
    'signature_id': 'signature_id1',
    'doc_id': 'doc_id1',
    'doc_type': 'cargo',
    'signer_id': 'signer_id1',
    'properties': {
        'sign_type': 'confirmation_code',
        'send_properties': [{'send_type': 'ucommunications_sms'}],
    },
    'signer_type': 'sender',
    'idempotency_token': '2',
}

REQ_BODY_3 = {
    'signature_id': 'signature_id1',
    'doc_id': 'doc_id1',
    'doc_type': 'cargo',
    'signer_id': 'signer_id1',
    'properties': {
        'sign_type': 'confirmation_code',
        'send_properties': [{'send_type': 'ucommunications_sms'}],
    },
    'signer_type': 'sender',
    'idempotency_token': '3',
}


async def test_sms_limit_per_signature(
        taxi_esignature_issuer, pgsql, get_req_headers, mock_ucommunications,
):
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=REQ_BODY, headers=get_req_headers(),
    )
    assert response.status_code == 200
    cursor = pgsql['esignature_issuer'].conn.cursor()
    cursor.execute(
        f'UPDATE esignature_issuer.signatures'
        ' SET sms_per_signature_count = 5',  # uses hardcoded val, watch out!
    )
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create',
        json={
            'signature_id': 'signature_id1',
            'doc_id': 'doc_id1',
            'doc_type': 'cargo',
            'signer_id': 'signer_id1',
            'properties': {
                'sign_type': 'confirmation_code',
                'send_properties': [{'send_type': 'ucommunications_sms'}],
            },
            'signer_type': 'sender',
            'idempotency_token': '2',
        },
        headers=get_req_headers(),
    )
    assert response.status_code == 429
    assert (
        response.json()['message']
        == 'too many messages sent for this signature'
    )
    cursor.execute(
        f'UPDATE esignature_issuer.signatures'
        ' SET sms_per_signature_count = 4',  # uses hardcoded val, watch out!
    )
    cursor.execute(
        f'UPDATE esignature_issuer.signer_sms_counts'
        ' SET sms_last_sent_at = CURRENT_TIMESTAMP - interval \'10 second\' ',
    )
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=REQ_BODY_2, headers=get_req_headers(),
    )
    assert response.status_code == 200


async def test_sms_limit_per_day(
        taxi_esignature_issuer, pgsql, get_req_headers, mock_ucommunications,
):
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=REQ_BODY, headers=get_req_headers(),
    )
    assert response.status_code == 200
    cursor = pgsql['esignature_issuer'].conn.cursor()
    cursor.execute(
        f'UPDATE esignature_issuer.signer_sms_counts'
        ' SET sms_today_count = 50, sms_last_sent_at = CURRENT_TIMESTAMP',
    )
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=REQ_BODY_2, headers=get_req_headers(),
    )
    assert response.status_code == 429
    assert response.json()['message'] == 'too many messages sent this day'
    cursor.execute(
        f'UPDATE esignature_issuer.signer_sms_counts'
        ' SET sms_last_sent_at = make_timestamptz(2013, 7, 15, 8, 15, 23.5)',
    )
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=REQ_BODY_2, headers=get_req_headers(),
    )
    assert response.status_code == 200
    cursor.execute(
        f'UPDATE esignature_issuer.signer_sms_counts'
        ' SET sms_today_count = 49,'
        'sms_last_sent_at = CURRENT_TIMESTAMP - interval \'7 second\'',
    )
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=REQ_BODY_3, headers=get_req_headers(),
    )
    assert response.status_code == 200


async def test_sms_delay(
        taxi_esignature_issuer, pgsql, mock_ucommunications, get_req_headers,
):
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=REQ_BODY, headers=get_req_headers(),
    )
    assert response.status_code == 200
    cursor = pgsql['esignature_issuer'].conn.cursor()
    cursor.execute(
        f'UPDATE esignature_issuer.signer_sms_counts'
        ' SET sms_today_count = 1, sms_last_sent_at = CURRENT_TIMESTAMP',
    )
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=REQ_BODY_2, headers=get_req_headers(),
    )
    assert response.status_code == 429
    assert response.json()['message'] == 'wait a few seconds to retry'
    cursor.execute(
        f'UPDATE esignature_issuer.signer_sms_counts'
        ' SET sms_last_sent_at = CURRENT_TIMESTAMP - interval \'10 second\'',
    )
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=REQ_BODY_2, headers=get_req_headers(),
    )
    assert response.status_code == 200
