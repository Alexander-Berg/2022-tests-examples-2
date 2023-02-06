import pytest

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


async def test_create(
        taxi_esignature_issuer,
        pgsql,
        testpoint,
        get_req_headers,
        mock_ucommunications,
):
    @testpoint('test_retry_in_create_handler')
    def point1(data):
        pass

    @testpoint('test_new_signature_in_create_handler')
    def point2(data):
        pass

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=REQ_BODY, headers=get_req_headers(),
    )
    assert response.status_code == 200

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=REQ_BODY, headers=get_req_headers(),
    )
    assert point1.has_calls
    assert response.status_code == 200

    # sms-limits fix
    cursor = pgsql['esignature_issuer'].conn.cursor()
    cursor.execute(
        f'UPDATE esignature_issuer.signer_sms_counts'
        ' SET sms_last_sent_at = make_timestamptz(2011, 11, 11, 11, 11, 11.0)',
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
    assert point2.has_calls
    assert response.status_code == 200


@pytest.mark.parametrize(
    'properties,expected_response',
    (
        pytest.param(
            {
                'sign_type': 'confirmation_code',
                'send_properties': [{'send_type': 'ucommunications_sms'}],
            },
            404,
            id='no_api',
        ),
        pytest.param(
            {
                'sign_type': 'confirmation_code',
                'send_properties': [
                    {'send_type': 'ucommunications_sms'},
                    {'send_type': 'api'},
                ],
            },
            200,
            id='allow_api',
        ),
    ),
)
async def test_api(
        taxi_esignature_issuer,
        create_signature,
        pgsql,
        mock_ucommunications,
        get_req_headers,
        properties,
        expected_response,
):
    req_body = REQ_BODY.copy()
    req_body['properties'] = properties
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=req_body, headers=get_req_headers(),
    )
    assert response.status_code == 200

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/confirmation-code',
        json={
            'signature_id': req_body['signature_id'],
            'doc_type': req_body['doc_type'],
            'doc_id': req_body['doc_id'],
        },
        headers=get_req_headers(),
    )
    assert response.status_code == expected_response


async def test_no_replace_existing(
        taxi_esignature_issuer,
        testpoint,
        get_req_headers,
        mock_ucommunications,
        pgsql,
):
    @testpoint('test_no_replace_existing')
    def testpoint_no_replace_existing(data):
        pass

    req_body = REQ_BODY.copy()
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=req_body, headers=get_req_headers(),
    )
    assert response.status_code == 200

    # sms-limits fix
    cursor = pgsql['esignature_issuer'].conn.cursor()
    cursor.execute(
        f'UPDATE esignature_issuer.signer_sms_counts'
        ' SET sms_last_sent_at = make_timestamptz(2011, 11, 11, 11, 11, 11.0)',
    )

    req_body['no_replace_existing'] = True
    req_body['idempotency_token'] = '2'
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=req_body, headers=get_req_headers(),
    )
    assert response.status_code == 200
    assert testpoint_no_replace_existing.has_calls


async def test_bad_signer_id(
        taxi_esignature_issuer, get_req_headers, mock_ucommunications,
):
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=REQ_BODY, headers=get_req_headers(),
    )
    assert response.status_code == 200

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create',
        json={
            'signature_id': 'signature_id1',
            'doc_id': 'doc_id1',
            'doc_type': 'cargo',
            'signer_id': 'signer_id2',
            'properties': {
                'sign_type': 'confirmation_code',
                'send_properties': [{'send_type': 'ucommunications_sms'}],
            },
            'signer_type': 'sender',
            'idempotency_token': '2',
        },
        headers=get_req_headers(),
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'bad_signer_id'


async def test_already_confirmed(
        taxi_esignature_issuer, get_req_headers, pgsql, mock_ucommunications,
):
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=REQ_BODY, headers=get_req_headers(),
    )
    assert response.status_code == 200

    cursor = pgsql['esignature_issuer'].conn.cursor()
    cursor.execute(
        f'UPDATE esignature_issuer.signatures'
        ' SET signed_at = CURRENT_TIMESTAMP',
    )

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create',
        json={**REQ_BODY, 'idempotency_token': '2'},
        headers=get_req_headers(),
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'already_confirmed'


@pytest.mark.config(
    PASSPORT_SMS_LOCALE_MAPPING={'__default__': 'jp', 'ru': 'ru', 'by': 'fr'},
)
@pytest.mark.parametrize(
    'locale,expected', [('ru', 'ru'), ('by', 'fr'), ('fr', 'jp')],
)
async def test_passport_locale_mapping(
        taxi_esignature_issuer, mockserver, get_req_headers, locale, expected,
):
    @mockserver.json_handler('/ucommunications/general/sms/send')
    def _submit(request):
        assert request.json['locale'] == expected
        return {
            'message': 'OK',
            'code': '200',
            'message_id': 'f13bb985ce7549b181061ed3e6ad1286',
            'status': 'sent',
        }

    req_headers = get_req_headers(locale)
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=REQ_BODY, headers=req_headers,
    )
    assert response.status_code == 200


@pytest.mark.usefixtures('mock_ucommunications_429')
@pytest.mark.parametrize(
    'expected_code',
    [
        pytest.param(
            429,
            marks=[
                pytest.mark.config(
                    ESIGNATURE_ISSUER_NO_THROW_ON_SMS_FAILURE=False,
                ),
            ],
        ),
        pytest.param(
            200,
            marks=[
                pytest.mark.config(
                    ESIGNATURE_ISSUER_NO_THROW_ON_SMS_FAILURE=True,
                ),
            ],
        ),
    ],
)
async def test_general_sms_send_failure(
        taxi_esignature_issuer, get_req_headers, expected_code,
):
    req_headers = get_req_headers()
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=REQ_BODY, headers=req_headers,
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'send_smd',
    [
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    ESIGNATURE_ISSUER_SEND_SMS_WITH_USER_CODE=False,
                ),
            ],
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    ESIGNATURE_ISSUER_SEND_SMS_WITH_USER_CODE=True,
                ),
            ],
        ),
    ],
)
async def test_user_code(
        taxi_esignature_issuer,
        create_signature,
        pgsql,
        mock_ucommunications,
        get_req_headers,
        send_smd,
):
    req_body = REQ_BODY.copy()
    req_body['properties']['send_properties'].append({'send_type': 'api'})
    req_body['user_code'] = 'qwerty123'
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=req_body, headers=get_req_headers(),
    )
    assert response.status_code == 200

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/confirmation-code',
        json={
            'signature_id': req_body['signature_id'],
            'doc_type': req_body['doc_type'],
            'doc_id': req_body['doc_id'],
        },
        headers=get_req_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {'code': 'qwerty123', 'attempts': 5}

    if send_smd:
        assert mock_ucommunications.times_called == 1
    else:
        assert mock_ucommunications.times_called == 0
