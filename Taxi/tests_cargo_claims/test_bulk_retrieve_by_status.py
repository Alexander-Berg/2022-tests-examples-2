import pytest


FIELDS_FOR_STATUSES = {
    'new': ['request_id', 'status', 'version', 'user_request_revision'],
    'accepted': ['request_id'],
}

HANDLERS_FOR_STATUSES = {'new': 'list/ready-for-estimate'}


@pytest.mark.parametrize(
    'requests, status, limit',
    [
        (
            [
                {
                    'request_id': 'request_id_1',
                    'corp_client_id': '012345678901234567890123456789_1',
                    'status': 'new',
                    'version': 1,
                    'user_request_revision': '1',
                },
                {
                    'request_id': 'request_id_2',
                    'corp_client_id': '012345678901234567890123456789_2',
                    'status': 'accepted',
                    'version': 1,
                    'user_request_revision': '1',
                },
            ],
            'new',
            1,
        ),
        (
            [
                {
                    'request_id': 'request_id_1',
                    'corp_client_id': '012345678901234567890123456789_1',
                    'status': 'new',
                    'version': 1,
                    'user_request_revision': '1',
                },
                {
                    'request_id': 'request_id_2',
                    'corp_client_id': '012345678901234567890123456789_3',
                    'status': 'new',
                    'version': 1,
                    'user_request_revision': '1',
                },
                {
                    'request_id': 'request_id_3',
                    'corp_client_id': '012345678901234567890123456789_3',
                    'status': 'new',
                    'version': 1,
                    'user_request_revision': '1',
                },
            ],
            'new',
            2,
        ),
    ],
)
async def test_bulk_retrieve(
        taxi_cargo_claims,
        state_controller,
        get_default_headers,
        get_default_request,
        requests,
        status,
        limit,
):
    def create_response_object(request, claim_id_by_idempotency_token):
        result = {}
        for key in FIELDS_FOR_STATUSES[status]:
            if key == 'request_id':
                result['id'] = claim_id_by_idempotency_token[request[key]]
            else:
                result[key] = request[key]
                result['skip_client_notify'] = False
        return result

    claim_id_by_idempotency_token = {}
    for request_index, request in enumerate(requests):
        state_controller.set_options(
            claim_index=request_index,
            corp_client_id=request['corp_client_id'],
            request_id=request['request_id'],
        )
        request_body = get_default_request()
        request_body['corp_client_id'] = request['corp_client_id']

        handlers_context = state_controller.handlers(claim_index=request_index)

        create_context = handlers_context.create
        create_context.params = {'request_id': request['request_id']}
        create_context.request = request_body

        claim_info = await state_controller.apply(
            target_status=request['status'], claim_index=request_index,
        )
        claim_id = claim_info.claim_id

        claim_id_by_idempotency_token[request['request_id']] = claim_id

    response = await taxi_cargo_claims.post(
        'v1/claims/{}'.format(HANDLERS_FOR_STATUSES[status]),
        json={'limit': limit},
    )
    claims = filter(lambda x: x['status'] == status, requests)

    assert response.status_code == 200
    assert response.json() == {
        'claims': [
            create_response_object(request, claim_id_by_idempotency_token)
            for request in list(claims)[:limit]
        ],
    }
