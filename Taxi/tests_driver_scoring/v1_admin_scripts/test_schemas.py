import tests_driver_scoring.tvm_tickets as tvm_tickets


async def test_v1_admin_schemas_get_default_ok(taxi_driver_scoring, load_json):
    response = await taxi_driver_scoring.get(
        'v1/admin/scripts/schemas',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
    )
    assert response.status_code == 200
    assert load_json('contexts.json') == response.json()


async def test_v1_admin_schemas_get_order_context_ok(
        taxi_driver_scoring, load_json,
):
    response = await taxi_driver_scoring.get(
        'v1/admin/scripts/schemas?names=order_context',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
    )
    assert response.status_code == 200
    assert load_json('order_context.json') == response.json()


async def test_additional_public_schemas(taxi_driver_scoring, load_json):
    response = await taxi_driver_scoring.get(
        'v1/admin/scripts/schemas?names=ScoredOrder,order_contexts',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
    )
    assert response.status_code == 200
    assert response.json() == load_json('scored_order.json')


async def test_v1_admin_schemas_get_not_found(taxi_driver_scoring):
    response = await taxi_driver_scoring.get(
        'v1/admin/scripts/schemas?names=abc,order_context,xyz',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
    )
    assert response.status_code == 404
    body = response.json()
    assert body['code'] == '404'
    assert body['names'] == ['abc', 'xyz']


async def test_v1_admin_schemas_get_candidate_and_tags_ok(
        taxi_driver_scoring, load_json,
):
    response = await taxi_driver_scoring.get(
        'v1/admin/scripts/schemas?names=Candidate,Tags',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
    )
    assert response.status_code == 200
    assert response.json() == load_json('candidate_tags.json')
