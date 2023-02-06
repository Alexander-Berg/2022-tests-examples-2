import copy

import pytest


CREATE_REQ_BODY = {
    'signature_id': 'signature_id1',
    'doc_id': 'doc_id1',
    'doc_type': 'cargo',
    'signer_id': 'signer_id1',
    'signer_type': 'sender',
    'properties': {
        'sign_type': 'confirmation_code',
        'send_properties': [{'send_type': 'ucommunications_sms'}],
    },
    'idempotency_token': '1',
}

CONFIRM_REQ_BODY = {
    'signature_id': 'signature_id1',
    'doc_type': 'cargo',
    'doc_id': 'doc_id1',
    'code': 'incorrect-code',
}


@pytest.mark.config(ESIGNATURE_ISSUER_ENABLE_SKIP_CHECK=True)
@pytest.mark.parametrize('skip_check', [True, False, None])
async def test_confirm_skip_check(
        taxi_esignature_issuer,
        get_req_headers,
        mock_ucommunications,
        skip_check,
):
    body = copy.deepcopy(CREATE_REQ_BODY)
    if skip_check is not None:
        body['skip_check'] = skip_check
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=body, headers=get_req_headers(),
    )
    assert response.json() == {}
    assert response.status_code == 200

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/confirm',
        json=CONFIRM_REQ_BODY,
        headers=get_req_headers(),
    )
    assert response.status_code == 200
    if skip_check:
        assert response.json()['status'] == 'ok'
    else:
        assert response.json()['status'] == 'invalid_code'


@pytest.mark.config(ESIGNATURE_ISSUER_ENABLE_SKIP_CHECK=False)
@pytest.mark.parametrize('skip_check', [True, False, None])
async def test_confirm_skip_check_disabled(
        pgsql,
        taxi_esignature_issuer,
        get_req_headers,
        mock_ucommunications,
        skip_check,
):
    body = copy.deepcopy(CREATE_REQ_BODY)
    if skip_check is not None:
        body['skip_check'] = skip_check
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=body, headers=get_req_headers(),
    )
    assert response.status_code == 400 if skip_check else 200

    response = await taxi_esignature_issuer.post(
        '/v1/signatures/confirm',
        json=CONFIRM_REQ_BODY,
        headers=get_req_headers(),
    )
    if skip_check:
        # shouldn't be created
        assert response.status_code == 404
        assert response.json()['code'] == 'not_found'
    else:
        assert response.status_code == 200
        assert response.json()['status'] == 'invalid_code'


@pytest.mark.config(ESIGNATURE_ISSUER_ENABLE_SKIP_CHECK=True)
@pytest.mark.parametrize('skip_check', [True, False])
async def test_confirm_skip_check_mismatch(
        taxi_esignature_issuer,
        pgsql,
        get_req_headers,
        mock_ucommunications,
        get_correct_code,
        skip_check,
        taxi_config,
):
    body = copy.deepcopy(CREATE_REQ_BODY)
    body['skip_check'] = skip_check
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/create', json=body, headers=get_req_headers(),
    )
    assert response.status_code == 200

    taxi_config.set_values(dict(ESIGNATURE_ISSUER_ENABLE_SKIP_CHECK=False))
    await taxi_esignature_issuer.invalidate_caches()

    request = copy.deepcopy(CONFIRM_REQ_BODY)
    if not skip_check:
        request['code'] = get_correct_code(
            request['signature_id'], request['doc_type'], request['doc_id'],
        )
    response = await taxi_esignature_issuer.post(
        '/v1/signatures/confirm', json=request, headers=get_req_headers(),
    )
    if skip_check:
        # shouldn't be created
        assert response.status_code == 409
        assert response.json()['code'] == 'skip_signature_disabled'
    else:
        assert response.status_code == 200
        assert response.json()['status'] == 'ok'
