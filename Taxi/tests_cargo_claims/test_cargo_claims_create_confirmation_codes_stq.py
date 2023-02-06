from . import utils_v2


async def test_stq_claim_v2(stq_runner, state_controller, mockserver):
    state_controller.use_create_version('v2')

    request = utils_v2.get_create_request()
    for point in request['route_points']:
        point['skip_confirmation'] = False
    request['route_points'][0]['pickup_code'] = '123456'
    state_controller.handlers().create.request = request

    state_controller.handlers().create.request = request

    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id

    @mockserver.json_handler('/esignature-issuer/v1/signatures/bulk-create')
    def _request(request):
        assert request.json == [
            {
                'doc_id': claim_id,
                'doc_type': 'cargo_claims',
                'signature_id': 'sender_to_driver_1000',
                'signer_id': '+79999999991_id',
                'signer_type': 'sender_to_driver',
                'idempotency_token': f'claim_{claim_id}_create_only',
                'properties': {
                    'send_properties': [],
                    'sign_type': 'confirmation_code',
                },
                'user_code': '123456',
            },
            {
                'doc_id': claim_id,
                'doc_type': 'cargo_claims',
                'signature_id': 'driver_to_return_1003',
                'signer_id': '+79999999994_id',
                'signer_type': 'driver_to_return',
                'idempotency_token': f'claim_{claim_id}_create_only',
                'properties': {
                    'send_properties': [],
                    'sign_type': 'confirmation_code',
                },
            },
        ]
        return mockserver.make_response(status=200)

    await stq_runner.cargo_claims_create_confirmation_codes.call(
        task_id=claim_id, kwargs={'claim_uuid': claim_id}, expect_fail=False,
    )


async def test_stq_claim_v1(
        stq_runner, state_controller, get_default_request, mockserver,
):
    request = get_default_request()
    request['route_points']['source']['skip_confirmation'] = False
    request['route_points']['return']['skip_confirmation'] = True

    state_controller.handlers().create.request = request

    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id

    @mockserver.json_handler('/esignature-issuer/v1/signatures/bulk-create')
    def _request(request):
        assert request.json == [
            {
                'doc_id': claim_id,
                'doc_type': 'cargo_claims',
                'signature_id': 'sender_to_driver',
                'signer_id': '+71111111111_id',
                'signer_type': 'sender_to_driver',
                'idempotency_token': f'claim_{claim_id}_create_only',
                'properties': {
                    'send_properties': [],
                    'sign_type': 'confirmation_code',
                },
            },
        ]
        return mockserver.make_response(status=200)

    await stq_runner.cargo_claims_create_confirmation_codes.call(
        task_id=claim_id, kwargs={'claim_uuid': claim_id}, expect_fail=False,
    )


async def test_skip_confirmation(
        stq_runner, state_controller, get_default_request, mockserver,
):
    request = get_default_request()
    request['route_points']['source']['skip_confirmation'] = True
    request['route_points']['return']['skip_confirmation'] = True

    state_controller.handlers().create.request = request

    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id

    @mockserver.json_handler('/esignature-issuer/v1/signatures/bulk-create')
    def _request(_):
        assert False, 'Expect no requests to esignature'

    await stq_runner.cargo_claims_create_confirmation_codes.call(
        task_id=claim_id, kwargs={'claim_uuid': claim_id}, expect_fail=False,
    )
