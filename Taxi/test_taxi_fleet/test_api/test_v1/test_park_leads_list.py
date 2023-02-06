import aiohttp.web

PDS_AND_PHONES = [
    ('d717256f1a244e1e8bfd44b65b99c932', '+79112223301'),
    ('4d522330f757406a9beb4625d5fdaa79', '+79112223302'),
    ('a6aeb542700a4e2f82252a399bbe5184', '+79112223303'),
]


async def test_success(
        web_app_client,
        load_json,
        headers,
        mock_hiring_api,
        mock_personal_bulk_phones,
):
    stub = load_json('success.json')

    @mock_hiring_api('/v1/infranaim-mongo/tickets')
    async def _list(request):
        assert request.method.upper() == 'GET'
        assert request.query == stub['hiring_candidates_request']
        return aiohttp.web.json_response(stub['hiring_candidates_response'])

    mock_personal_bulk_phones(PDS_AND_PHONES)

    response = await web_app_client.post(
        '/api/v1/park-leads/list',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


async def test_success_with_filter_by_phone(
        web_app_client,
        load_json,
        headers,
        mock_hiring_api,
        mock_personal_bulk_phones,
        mock_personal_single_phone,
):

    stub = load_json('success_with_filter_by_phone.json')

    mock_personal_single_phone(
        '+79112223301', 'd717256f1a244e1e8bfd44b65b99c932',
    )

    @mock_hiring_api('/v1/infranaim-mongo/tickets')
    async def _list(request):
        assert request.method.upper() == 'GET'
        assert request.query == stub['hiring_candidates_request']
        return aiohttp.web.json_response(stub['hiring_candidates_response'])

    mock_personal_bulk_phones(PDS_AND_PHONES)

    response = await web_app_client.post(
        '/api/v1/park-leads/list',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={'phone': '+79112223301'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
