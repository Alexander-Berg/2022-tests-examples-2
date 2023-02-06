import pytest


def build_act(claim_id, claim_db_id):
    # 4 first chars in claim_id and hex claim_db_id
    return f'{claim_id[:4]}{claim_db_id:x}'


@pytest.mark.config(
    CARGO_CLAIMS_USE_IDENTITY_DOCS={
        'enabled': True,
        'types_priority': [],
        'excluded_types': [],
    },
)
async def test_act_generate(
        state_controller, stq_runner, pgsql, mockserver, mds_s3_storage,
):
    state_controller.use_create_version('v2_cargo_c2c')
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id

    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        'SELECT id '
        'FROM cargo_claims.claims WHERE uuid_id =\'%s\'' % claim_id,
    )
    (claim_db_id,) = list(cursor)[0]
    status = claim_info.current_state.status

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

    @mockserver.json_handler(
        '/driver-profiles/v1/identity-docs/retrieve_by_park_driver_profile_id',
    )
    def _mock_driver_profiles_identity_docs(request):
        assert 'park_driver_profile_id_in_set' in request.json
        response = {'docs_by_park_driver_profile_id': []}
        for key in request.json['park_driver_profile_id_in_set']:
            response['docs_by_park_driver_profile_id'].append(
                {'park_driver_profile_id': key, 'docs': []},
            )
        return response

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
                    'geodata': {'lat': 12, 'lon': 13, 'zoom': 0},
                },
            ],
        }

    @mockserver.json_handler('/cargo-waybill/v1/handover-act/generate-pdf')
    def _mock_waybill_generate(request):
        request_json = request.json
        request_json['act'].pop('date')
        assert request_json == {
            'act': {'id': build_act(claim_id, claim_db_id)},
            'driver': {
                'full_name': 'Kostya',
                'passport_information': '',
                'park_name': 'some park org name',
            },
            'company': {'legal_entity_name': 'ООО «Яндекс.Такси»'},
            'shipments': [
                {
                    'id': '1',
                    'shipment_items': [
                        {'name': '1. item title 1', 'number_of_packages': 2},
                    ],
                    'address': '2',
                },
                {
                    'id': '2',
                    'shipment_items': [
                        {'name': '2. item title 2', 'number_of_packages': 2},
                    ],
                    'address': '3',
                },
            ],
            'source_points': [
                {
                    'contact_person': 'string',
                    'contact_signature': 'signatures.sender',
                    'driver_signature': 'signatures.carrier',
                    'shipment_id': '1, 2',
                },
            ],
            'destination_points': [
                {
                    'contact_person': 'string',
                    'contact_signature': 'signatures.client',
                    'driver_signature': 'signatures.carrier',
                    'shipment_id': '1',
                },
                {
                    'contact_person': 'string',
                    'contact_signature': 'signatures.client',
                    'driver_signature': 'signatures.carrier',
                    'shipment_id': '2',
                },
            ],
            'return_points': [],
        }

        return mockserver.make_response(
            b'PDF FILE MOCK', content_type='application/pdf',
        )

    await stq_runner.cargo_claims_documents_store.call(
        task_id=f'{claim_id}_act',
        args=[f'{claim_id}', 'act'],
        kwargs={'status': status},
    )
