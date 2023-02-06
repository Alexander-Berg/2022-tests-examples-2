REMOTE_IP = '127.0.0.1'


async def test_get_customer_ip_v2(
        claim_creator_v2,
        get_default_headers,
        build_create_request,
        get_claim_v2,
):
    request, _ = build_create_request(use_create_v2=True)

    headers = get_default_headers()
    headers['X-Remote-IP'] = REMOTE_IP

    response = await claim_creator_v2(request, headers=headers)
    assert response.status_code == 200
    claim = response.json()

    claim = await get_claim_v2(claim['id'])
    assert claim['customer_ip'] == REMOTE_IP


async def test_get_customer_ip_v1(
        claims_creator, get_default_headers, get_claim_v2, mock_create_event,
):
    mock_create_event()
    headers = get_default_headers()
    headers['X-Remote-IP'] = REMOTE_IP

    response = await claims_creator['v1'](headers=headers)

    claim = await get_claim_v2(response.claim_id)
    assert claim['customer_ip'] == REMOTE_IP
