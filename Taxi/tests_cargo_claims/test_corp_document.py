import pytest


CLAIM_STATUS = 'pickuped'


async def do_test(taxi_cargo_claims, claim_id, get_default_headers):
    response = await taxi_cargo_claims.get(
        f'/api/integration/v2/claims/document/?claim_id='
        f'{claim_id}&document_type=act'
        f'&version=1&status={CLAIM_STATUS}',
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.content == b'PDF FILE MOCK'

    # wrong status
    response = await taxi_cargo_claims.get(
        f'/api/integration/v2/claims/document/?claim_id='
        f'{claim_id}&document_type=act'
        f'&version=1&status=new',
        headers=get_default_headers(),
    )
    assert response.status_code == 409

    # wrong version
    response = await taxi_cargo_claims.get(
        f'/api/integration/v2/claims/document/?claim_id='
        f'{claim_id}&document_type=act'
        f'&version=110&status={CLAIM_STATUS}',
        headers=get_default_headers(),
    )
    assert response.status_code == 409

    # wrong corp id
    response = await taxi_cargo_claims.get(
        f'/api/integration/v2/claims/document/?claim_id='
        f'{claim_id}&document_type=act'
        f'&version=1&status={CLAIM_STATUS}',
        headers=get_default_headers('other_corp_id0123456789012345678'),
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
                        '__default__': {
                            'enabled': True,
                            'yt-use-runtime': False,
                            'yt-timeout-ms': 1000,
                            'ttl-days': 3650,
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
                        '__default__': {'enabled': False},
                    },
                ),
            ],
        ),
    ],
)
async def test_corp_get_document(
        taxi_cargo_claims,
        mockserver,
        state_controller,
        get_default_headers,
        stq,
        stq_runner,
):
    # TODO move to prepare_state
    @mockserver.json_handler('/esignature-issuer/v1/signatures/list')
    def _mock_esignature_issuer(request):
        return {
            'doc_type': request.json['doc_type'],
            'doc_id': request.json['doc_id'],
            'signatures': [
                {
                    'signature_id': 'sender_to_driver_1',
                    'signer_id': '+79999999991_id',
                    'sign_type': 'ya_sms',
                    'signed_at': '2020-04-09T17:33:23.825194+00:00',
                },
                {
                    'signature_id': 'driver_to_recipient_2',
                    'signer_id': '+79999999992_id',
                    'sign_type': 'ya_sms',
                    'signed_at': '2020-04-09T17:33:23.825194+00:00',
                },
                {
                    'signature_id': 'driver_to_recipient_3',
                    'signer_id': '+79999999993_id',
                    'sign_type': 'ya_sms',
                    'signed_at': '2020-04-09T17:33:23.825194+00:00',
                },
            ],
        }

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks_list(request):
        return {
            'parks': [
                {
                    'id': 'park_id',
                    'login': 'login',
                    'is_active': True,
                    'city_id': 'city',
                    'locale': 'locale',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'demo_mode': False,
                    'country_id': 'country_id',
                    'name': 'some park name',
                    'org_name': 'some park org name',
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    @mockserver.json_handler('/cargo-waybill/v1/handover-act/generate-pdf')
    def _mock_waybill_generate(request):
        request_json = request.json
        request_json['act'].pop('date')

        return mockserver.make_response(
            b'PDF FILE MOCK', content_type='application/pdf',
        )

    claim_info = await state_controller.apply(target_status=CLAIM_STATUS)
    claim_id = claim_info.claim_id

    times_called_expected = 2
    assert (
        stq.cargo_claims_documents_store.times_called == times_called_expected
    )
    for _ in range(times_called_expected):
        stq_params = stq.cargo_claims_documents_store.next_call()
        await stq_runner.cargo_claims_documents_store.call(
            task_id=stq_params['id'],
            args=stq_params['args'],
            kwargs=stq_params['kwargs'],
        )

    await do_test(taxi_cargo_claims, claim_id, get_default_headers)
