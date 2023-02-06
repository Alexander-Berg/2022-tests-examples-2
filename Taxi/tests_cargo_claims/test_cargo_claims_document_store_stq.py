import datetime
import json
import uuid

import pytest

from . import utils_v2


DOC_NUMBER = '1234567890'

DOC_DATA = {'number': DOC_NUMBER}


@pytest.mark.config(
    CARGO_CLAIMS_USE_IDENTITY_DOCS={
        'enabled': True,
        'types_priority': [],
        'excluded_types': [],
    },
)
@pytest.mark.parametrize(
    'expect_fail',
    (
        pytest.param(
            True, marks=pytest.mark.config(CARGO_CLAIMS_TEST_CORP_CLIENTS=[]),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                CARGO_CLAIMS_TEST_CORP_CLIENTS=[
                    '01234567890123456789012345678912',
                ],
            ),
        ),
    ),
)
async def test_no_contract(
        mockserver,
        state_controller,
        stq,
        stq_runner,
        pgsql,
        expect_fail: bool,
):
    status = 'performer_found'
    claim_info = await state_controller.apply(target_status=status)
    claim_id = claim_info.claim_id

    @mockserver.json_handler('/billing-replication/contract/')
    def _contract(request):
        return []

    @mockserver.json_handler('/billing-replication/person/')
    def _person(request):
        return []

    await stq_runner.cargo_claims_documents_store.call(
        task_id=f'{claim_id}_act',
        args=[claim_id, 'act'],
        kwargs={'status': status},
        expect_fail=expect_fail,
    )

    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        f"""
SELECT last_fail_reason FROM cargo_claims.documents ORDER BY claim_status
        """,
    )
    assert list(cursor)[0][0] == 'signed_contract_not_found'


@pytest.mark.parametrize(
    'driver_doc_types,expected_passport,expect_complete,'
    'created_ts,bad_person_id',
    [
        pytest.param(
            ['passport_rus'],
            '',
            False,
            datetime.datetime.utcnow() - datetime.timedelta(minutes=2),
            False,
            id='request_too_late',
            marks=pytest.mark.config(
                CARGO_CLAIMS_USE_IDENTITY_DOCS={
                    'enabled': True,
                    'types_priority': [],
                    'excluded_types': [],
                },
                CARGO_CLAIMS_DOCUMENTS_STORE_TIMEOUT=1,
            ),
        ),
        pytest.param(
            ['passport_rus'],
            '',
            True,
            datetime.datetime.utcnow(),
            False,
            id='identity_docs_disabled',
            marks=pytest.mark.config(
                CARGO_CLAIMS_USE_IDENTITY_DOCS={
                    'enabled': False,
                    'types_priority': [],
                    'excluded_types': [],
                },
            ),
        ),
        pytest.param(
            ['passport_rus'],
            'Паспорт РФ ' + DOC_NUMBER,
            True,
            None,
            False,
            id='identity_docs_enabled',
            marks=pytest.mark.config(
                CARGO_CLAIMS_USE_IDENTITY_DOCS={
                    'enabled': True,
                    'types_priority': [],
                    'excluded_types': [],
                },
            ),
        ),
        pytest.param(
            ['passport_rus'],
            'Паспорт РФ ' + DOC_NUMBER,
            False,
            None,
            True,
            id='identity_docs_enabled_bad_id',
            marks=pytest.mark.config(
                CARGO_CLAIMS_USE_IDENTITY_DOCS={
                    'enabled': True,
                    'types_priority': [],
                    'excluded_types': [],
                },
            ),
        ),
        pytest.param(
            ['passport_rus', 'passport_arm'],
            'Паспорт РФ ' + DOC_NUMBER,
            True,
            None,
            False,
            id='identity_docs_excluded',
            marks=pytest.mark.config(
                CARGO_CLAIMS_USE_IDENTITY_DOCS={
                    'enabled': True,
                    'types_priority': [],
                    'excluded_types': ['passport_arm'],
                },
            ),
        ),
        pytest.param(
            ['passport_arm', 'passport_rus'],
            'Паспорт РФ ' + DOC_NUMBER,
            True,
            None,
            False,
            id='identity_docs_priority',
            marks=pytest.mark.config(
                CARGO_CLAIMS_USE_IDENTITY_DOCS={
                    'enabled': True,
                    'types_priority': ['passport_rus'],
                    'excluded_types': [],
                },
            ),
        ),
        pytest.param(
            ['passport_arm', 'military_id_card', 'passport_rus'],
            'Паспорт РФ ' + DOC_NUMBER,
            True,
            None,
            False,
            id='identity_docs_priority_regexp',
            marks=pytest.mark.config(
                CARGO_CLAIMS_USE_IDENTITY_DOCS={
                    'enabled': True,
                    'types_priority': ['passport_rus', 'passport_*'],
                    'excluded_types': [],
                },
            ),
        ),
    ],
)
async def test_mds_sets_act(
        taxi_cargo_claims,
        mockserver,
        stq_runner,
        pgsql,
        state_controller,
        driver_doc_types,
        expected_passport,
        mds_s3_storage,
        get_default_driver_auth_headers,
        get_default_corp_client_id,
        expect_complete,
        created_ts,
        bad_person_id,
):
    status = 'performer_found'
    claim_info = await state_controller.apply(target_status=status)
    claim_id = claim_info.claim_id

    driver_id = state_controller.get_flow_context().driver_id
    park_id = state_controller.get_flow_context().park_id

    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        'INSERT INTO cargo_claims.corp_client_names '
        '(corp_client_id, full_name, short_name) '
        'VALUES (\'%s\', \'%s\', \'%s\')'
        % (get_default_corp_client_id, 'ООО КАРГО_full', 'ООО КАРГО_short'),
    )

    @mockserver.json_handler('/billing-replication/contract/')
    def _contract(request):
        return [
            {
                'ID': 100,
                'IS_ACTIVE': 1,
                'EXTERNAL_ID': '42131 /12',
                'DT': '01-01-2020',
                'SERVICES': [650, 35],
                'PERSON_ID': 239 if bad_person_id else 100,
            },
        ]

    @mockserver.json_handler('/billing-replication/person/')
    def _person(request):
        return [
            {
                'ID': '99',
                'LONGNAME': 'ООО КАРГО_full_99',
                'NAME': 'ООО КАРГО_short_99',
            },
            {
                'ID': '100',
                'LONGNAME': 'ООО КАРГО_full_100',
                'NAME': 'ООО КАРГО_short_100',
            },
            {
                'ID': '101',
                'LONGNAME': 'ООО КАРГО_full_101',
                'NAME': 'ООО КАРГО_short_101',
            },
        ]

    @mockserver.json_handler('/esignature-issuer/v1/signatures/list')
    def _mock_esignature_issuer(request):
        return {
            'doc_type': request.json['doc_type'],
            'doc_id': request.json['doc_id'],
            'signatures': [],
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

    @mockserver.json_handler(
        '/driver-profiles/v1/identity-docs/retrieve_by_park_driver_profile_id',
    )
    def _mock_driver_profiles_identity_docs(request):
        assert 'park_driver_profile_id_in_set' in request.json
        response = {'docs_by_park_driver_profile_id': []}
        for key in request.json['park_driver_profile_id_in_set']:
            (req_driver, req_park) = key.split('_', 1)
            docs = [
                {
                    'id': uuid.uuid4().hex,
                    'data': {
                        'driver_id': req_driver,
                        'park_id': req_park,
                        'type': driver_doc_type,
                        'data_pd_id': json.dumps(DOC_DATA) + '_id',
                        'number_pd_id': DOC_NUMBER + '_id',
                    },
                }
                for driver_doc_type in driver_doc_types
            ]
            response['docs_by_park_driver_profile_id'].append(
                {'park_driver_profile_id': key, 'docs': docs},
            )
        return response

    @mockserver.json_handler('/cargo-waybill/v1/handover-act/generate-pdf')
    def _mock_waybill_generate(request):
        assert request.json['client'] == {
            'contract_id': '42131 /12',
            'contract_date': '01-01-2020',
            'supplementary_agreement_id': '',
            'full_name': 'ООО КАРГО_full_100',
        }
        return mockserver.make_response(
            b'PDF FILE MOCK', content_type='application/pdf',
        )

    kwargs = {
        'claim_id': claim_id,
        'document_type': 'act',
        'status': status,
        'driver_id': driver_id,
        'park_id': park_id,
    }
    if created_ts is not None:
        kwargs['created_ts'] = created_ts
    await stq_runner.cargo_claims_documents_store.call(
        task_id=f'{claim_id}_act', kwargs=kwargs, expect_fail=bad_person_id,
    )

    response = await taxi_cargo_claims.post(
        '/v1/segments/get-document',
        json={
            'driver': {'driver_profile_id': driver_id, 'park_id': park_id},
            'document_type': 'act',
            'point_id': 1,
        },
    )
    if expect_complete:
        assert response.status_code == 200
        assert response.content == b'PDF FILE MOCK'
    else:
        assert response.status_code == 404


@pytest.mark.config(
    CARGO_CLAIMS_USE_IDENTITY_DOCS={
        'enabled': True,
        'types_priority': [],
        'excluded_types': [],
    },
    CARGO_SERVICE_IDS=[650, 718],
)
async def test_mds_sets_multipoint_act(
        taxi_cargo_claims,
        mockserver,
        state_controller,
        stq_runner,
        mds_s3_storage,
        get_default_driver_auth_headers,
):
    status = 'performer_found'
    claim_info = await state_controller.apply(target_status=status)
    claim_id = claim_info.claim_id

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
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 1},
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
            (req_driver, req_park) = key.split('_', 1)
            docs = [
                {
                    'id': uuid.uuid4().hex,
                    'data': {
                        'driver_id': req_driver,
                        'park_id': req_park,
                        'type': driver_doc_type,
                        'data_pd_id': json.dumps(DOC_DATA) + '_id',
                        'number_pd_id': DOC_NUMBER + '_id',
                    },
                }
                for driver_doc_type in ['passport_rus']
            ]
            response['docs_by_park_driver_profile_id'].append(
                {'park_driver_profile_id': key, 'docs': docs},
            )
        return response

    @mockserver.json_handler('/cargo-waybill/v1/handover-act/generate-pdf')
    def _mock_waybill_generate(request):
        return mockserver.make_response(
            b'PDF FILE MOCK', content_type='application/pdf',
        )

    await stq_runner.cargo_claims_documents_store.call(
        task_id=f'{claim_id}_act',
        args=[f'{claim_id}', 'act'],
        kwargs={'status': status},
    )

    response = await taxi_cargo_claims.post(
        '/v1/segments/get-document',
        json={
            'driver': {
                'driver_profile_id': (
                    state_controller.get_flow_context().driver_id
                ),
                'park_id': state_controller.get_flow_context().park_id,
            },
            'document_type': 'act',
            'point_id': 1,
        },
    )
    assert response.status_code == 200
    assert response.content == b'PDF FILE MOCK'


@pytest.mark.config(
    CARGO_CLAIMS_ACT_DOCUMENT_FINAL_STATUSES=['delivered', 'returned'],
)
async def test_delete_documents(
        taxi_cargo_claims,
        state_controller,
        stq,
        stq_runner,
        mockserver,
        testpoint,
        pgsql,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks_list(request):
        return {'parks': []}

    @mockserver.json_handler('/cargo-waybill/v1/handover-act/generate-pdf')
    def _mock_waybill_generate(request):
        return mockserver.make_response(
            b'PDF FILE MOCK', content_type='application/pdf',
        )

    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_s3(request):
        return mockserver.make_response(json={}, status=200)

    claim_info = await state_controller.apply(target_status='delivered')
    claim_id = claim_info.claim_id

    for status in ['performer_found', 'pickuped', 'delivered']:
        await stq_runner.cargo_claims_documents_store.call(
            task_id=f'{claim_id}_act',
            args=[claim_id, 'act'],
            kwargs={'status': status},
        )

    assert stq.cargo_claims_delete_act_documents.times_called == 1

    await stq_runner.cargo_claims_delete_act_documents.call(
        task_id=claim_id, args=[claim_id, 'act'],
    )

    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        f"""
SELECT is_deleted FROM cargo_claims.documents ORDER BY claim_status
        """,
    )
    assert list(cursor) == [(None,), (True,), (True,)]


@pytest.mark.parametrize(
    'phoenix_corp,payment_scheme,expect_complete',
    [(False, '', True), (True, 'decoupling', True), (True, 'agent', False)],
)
@pytest.mark.config(
    CARGO_CLAIMS_USE_IDENTITY_DOCS={
        'enabled': False,
        'types_priority': [],
        'excluded_types': [],
    },
)
async def test_phoenix_flow(
        taxi_cargo_claims,
        mockserver,
        stq_runner,
        state_controller,
        mock_cargo_corp_up,
        phoenix_corp,
        get_default_driver_auth_headers,
        expect_complete,
        payment_scheme,
):
    if payment_scheme == 'decoupling':
        mock_cargo_corp_up.is_agent_scheme = False
    state_controller.use_create_version('v2')
    state_controller.handlers().create.request = utils_v2.get_create_request()
    state_controller.set_options(is_phoenix_corp=phoenix_corp)
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id

    driver_id = state_controller.get_flow_context().driver_id
    park_id = state_controller.get_flow_context().park_id

    @mockserver.json_handler('/billing-replication/person/')
    def _person(request):
        return [
            {
                'ID': '100',
                'LONGNAME': 'ООО КАРГО_full_100',
                'NAME': 'ООО КАРГО_short_100',
            },
        ]

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
        assert request.json['client'] == {
            'contract_id': '42131 /12',
            'contract_date': '01-01-2020',
            'supplementary_agreement_id': '',
            'full_name': 'ООО КАРГО_full_100',
        }
        return mockserver.make_response(
            b'PDF FILE MOCK', content_type='application/pdf',
        )

    kwargs = {
        'claim_id': claim_id,
        'document_type': 'act',
        'status': 'performer_found',
        'driver_id': driver_id,
        'park_id': park_id,
        'created_ts': datetime.datetime.utcnow(),
    }
    await stq_runner.cargo_claims_documents_store.call(
        task_id=f'{claim_id}_act', kwargs=kwargs, expect_fail=False,
    )

    response = await taxi_cargo_claims.post(
        '/v1/segments/get-document',
        json={
            'driver': {'driver_profile_id': driver_id, 'park_id': park_id},
            'document_type': 'act',
            'point_id': 1,
        },
    )
    if expect_complete:
        assert response.status_code == 200
        assert response.content == b'PDF FILE MOCK'
    else:
        assert response.status_code == 404
