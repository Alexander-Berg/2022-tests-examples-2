import pytest

from testsuite.utils import http

from test_selfemployed import conftest


CONFIG_PARAMS = dict(
    SELFEMPLOYED_NONRESIDENT_SETTINGS={
        'account_prefix': '40820',
        'disabled_tag_name': 'nonresident_temporary_blocked',
        'eligible_banks': [{'bik': '040000000'}],
        'is_enabled': True,
        'use_stq': False,
    },
    SELFEMPLOYED_REQUISITES_SETTINGS={
        'bank': {
            'sf_subject': 'Self-Employed Change Payment Details',
            'resident_account_prefixes': ['40817'],
            'bik_prefixes': ['04'],
        },
        'sbp': {
            'sf_subject': 'Self-Employed FPS Change Payment Details',
            'banks': [
                {'id': 'test_bank', 'name': 'sbp_bank_name.test_bank'},
                {
                    'id': 'bad_bank',
                    'name': 'sbp_bank_name.bad_bank',
                    'disabled': True,
                },
            ],
        },
    },
    SELFEMPLOYED_SALESFORCE_CFG={
        'RecordTypeIds': {
            'Account': 'RecordTypeAccount',
            'Asset': 'RecordTypeAsset',
            'Case': 'RecordTypeCase',
            'Opportunity': 'RecordTypeOpportunity',
        },
    },
)


def _make_test_requested_exp_params(
        is_selfemployed, phone_pd_id, allow_sbp, is_resident,
):
    return dict(
        consumer='selfemployed/fns-se/requisites',
        experiment_name='selfemployed_allow_sbp',
        args=[
            {
                'name': 'is_selfemployed',
                'type': 'bool',
                'value': is_selfemployed,
            },
            {'name': 'is_selfreg', 'type': 'bool', 'value': False},
            {'name': 'is_resident', 'type': 'bool', 'value': is_resident},
            {'name': 'phone_pd_id', 'type': 'string', 'value': phone_pd_id},
            {'name': 'initial_park_id', 'type': 'string', 'value': 'parkid'},
            {
                'name': 'initial_contractor_id',
                'type': 'string',
                'value': 'contractorid',
            },
        ],
        value={'allow_sbp': allow_sbp},
    )


@pytest.mark.pgsql('selfemployed_main', files=['ownpark_metadata.sql'])
@pytest.mark.config(**CONFIG_PARAMS)
@pytest.mark.parametrize(
    'requisites,expected_code,expected_json',
    [
        pytest.param(
            {'type': 'bank', 'account': '40817312312312312312', 'bik': '1231'},
            409,
            {'code': 'BIK_VALIDATION_ERROR', 'text': 'error_incorrect_bik'},
            marks=pytest.mark.client_experiments3(
                **_make_test_requested_exp_params(
                    False, 'PHONE_PD_ID', True, True,
                ),
            ),
        ),
        pytest.param(
            {
                'type': 'bank',
                'account': '40817312312312312312',
                'bik': '123123123',
            },
            409,
            {'code': 'BIK_VALIDATION_ERROR', 'text': 'error_incorrect_bik'},
            marks=pytest.mark.client_experiments3(
                **_make_test_requested_exp_params(
                    False, 'PHONE_PD_ID', True, True,
                ),
            ),
        ),
        pytest.param(
            {
                'type': 'bank',
                'account': '40820312312312312312',
                'bik': '043123123',
            },
            409,
            {
                'code': 'NONRESIDENT_BANK_INELIGIBLE',
                'text': 'error_bank_not_eligible_for_nonresident',
            },
            marks=pytest.mark.client_experiments3(
                **_make_test_requested_exp_params(
                    False, 'PHONE_PD_ID', True, True,
                ),
            ),
        ),
        pytest.param(
            {'type': 'bank', 'account': '1231', 'bik': '043123123'},
            409,
            {
                'code': 'ACCOUNT_VALIDATION_ERROR',
                'text': 'error_incorrect_account_format',
            },
            marks=pytest.mark.client_experiments3(
                **_make_test_requested_exp_params(
                    False, 'PHONE_PD_ID', True, True,
                ),
            ),
        ),
        pytest.param(
            {'type': 'sbp', 'phone': '70123456789', 'bank_id': 'bad_bank'},
            409,
            {
                'code': 'BANK_VALIDATION_ERROR',
                'text': 'error_incorrect_bank_id',
            },
            marks=pytest.mark.client_experiments3(
                **_make_test_requested_exp_params(
                    False, 'PHONE_PD_ID', True, True,
                ),
            ),
        ),
        pytest.param(
            {'type': 'sbp', 'phone': '380123456789', 'bank_id': 'test_bank'},
            409,
            {
                'code': 'PHONE_VALIDATION_ERROR',
                'text': 'error_incorrect_phone_format',
            },
            marks=pytest.mark.client_experiments3(
                **_make_test_requested_exp_params(
                    False, 'PHONE_PD_ID', True, True,
                ),
            ),
        ),
        pytest.param(
            {'type': 'sbp', 'phone': '70123456789', 'bank_id': 'test_bank'},
            400,
            {
                'code': 'FORBIDDEN_REQUISITES_TYPE',
                'text': 'error_forbidden_requisites_type',
            },
            marks=pytest.mark.client_experiments3(
                **_make_test_requested_exp_params(
                    False, 'PHONE_PD_ID', False, True,
                ),
            ),
        ),
    ],
)
async def test_post_requisites_invalid(
        se_client, mock_salesforce, requisites, expected_code, expected_json,
):
    park_id = 'parkid'
    contractor_id = 'contractorid'

    @mock_salesforce('/services/data/v46.0/sobjects/Account/AccountId')
    async def _mock_get_account(request: http.Request):
        assert request.query == {'fields': 'Type,City__c,IBAN__c,SWIFT__c'}
        if requisites['type'] == 'bank':
            return {
                'Type': 'Selfemployed',
                'City__c': 'Москва',
                'IBAN__c': requisites['account'],
                'SWIFT__c': requisites['bik'],
            }
        return {
            'Type': 'Selfemployed',
            'City__c': 'Москва',
            'IBAN__c': requisites['phone'],
            'SWIFT__c': requisites['bank_id'],
        }

    response = await se_client.post(
        '/self-employment/fns-se/v3/requisites',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'requisites', 'requisites': requisites},
    )
    assert await response.json() == expected_json

    assert response.status == expected_code


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql('selfemployed_main', files=['ownpark_metadata.sql'])
@pytest.mark.parametrize(
    'requisites,sbp_enabled',
    [
        pytest.param(
            dict(type='bank', account='40817312312312312312', bik='043123123'),
            True,
            marks=pytest.mark.client_experiments3(
                **_make_test_requested_exp_params(
                    False, 'PHONE_PD_ID', True, True,
                ),
            ),
        ),  # Regular bank account
        pytest.param(
            dict(type='bank', account='40817312312312312312', bik='043123123'),
            False,
            marks=pytest.mark.client_experiments3(
                **_make_test_requested_exp_params(
                    False, 'PHONE_PD_ID', False, True,
                ),
            ),
        ),  # Regular bank account, SBP disabled
        pytest.param(
            dict(type='bank', account='40820312312312312312', bik='040000000'),
            True,
            marks=pytest.mark.client_experiments3(
                **_make_test_requested_exp_params(
                    False, 'PHONE_PD_ID', True, True,
                ),
            ),
        ),  # Nonresident bank account
        pytest.param(
            dict(type='sbp', phone='71231231231', bank_id='test_bank'),
            True,
            marks=pytest.mark.client_experiments3(
                **_make_test_requested_exp_params(
                    False, 'PHONE_PD_ID', True, True,
                ),
            ),
        ),  # SBP account
    ],
)
@pytest.mark.config(**CONFIG_PARAMS)
async def test_requisites(
        se_client,
        mock_salesforce,
        mock_personal,
        requisites,
        sbp_enabled,
        stq,
):
    park_id = 'parkid'
    contractor_id = 'contractorid'

    @mock_personal('/v1/tins/retrieve')
    async def _retrieve_inn_pd(request: http.Request):
        assert request.json == {'id': 'INN_PD_ID', 'primary_replica': False}
        return {'value': '000000', 'id': 'INN_PD_ID'}

    @mock_salesforce('/services/data/v46.0/sobjects/Case/')
    async def _mock_add_sobject(request: http.Request):
        if requisites['type'] == 'bank':
            assert request.json == {
                'RecordTypeId': 'RecordTypeCase',
                'AccountId': 'AccountId',
                'Status': 'In Progress',
                'Origin': 'API',
                'IBAN__c': requisites['account'],
                'SWIFT__c': requisites['bik'],
                'Subject': 'Self-Employed Change Payment Details',
            }
        else:
            assert request.json == {
                'RecordTypeId': 'RecordTypeCase',
                'AccountId': 'AccountId',
                'Status': 'In Progress',
                'Origin': 'API',
                'IBAN__c': requisites['phone'],
                'SWIFT__c': requisites['bank_id'],
                'Subject': 'Self-Employed FPS Change Payment Details',
            }
        return {'id': 'CaseId'}

    @mock_salesforce('/services/data/v46.0/sobjects/Case/CaseId')
    async def _mock_get_case(request: http.Request):
        assert request.query == {'fields': 'IBAN__c,SWIFT__c,Subject,Status'}
        if requisites['type'] == 'bank':
            return {
                'IBAN__c': requisites['account'],
                'SWIFT__c': requisites['bik'],
                'Subject': 'Self-Employed Change Payment Details',
                'Status': 'In Progress',
            }
        return {
            'IBAN__c': requisites['phone'],
            'SWIFT__c': requisites['bank_id'],
            'Subject': 'Self-Employed FPS Change Payment Details',
            'Status': 'In Progress',
        }

    @mock_salesforce('/services/data/v46.0/sobjects/Account/AccountId')
    async def _mock_get_account(request: http.Request):
        assert request.query == {'fields': 'Type,City__c,IBAN__c,SWIFT__c'}
        if requisites['type'] == 'bank':
            return {
                'Type': 'Selfemployed',
                'City__c': 'Москва',
                'IBAN__c': requisites['account'],
                'SWIFT__c': requisites['bik'],
            }
        return {
            'Type': 'Selfemployed',
            'City__c': 'Москва',
            'IBAN__c': requisites['phone'],
            'SWIFT__c': requisites['bank_id'],
        }

    response = await se_client.post(
        '/self-employment/fns-se/v3/requisites',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'requisites', 'requisites': requisites},
    )
    assert await response.json() == {
        'next_step': 'finish',
        'step_count': 7,
        'step_index': 7,
    }
    assert response.status == 200

    response = await se_client.get(
        '/self-employment/fns-se/v3/requisites',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
    )
    content = await response.json()
    assert content == {
        'base_ui': {
            'btn_next_text': 'Далее',
            'description': 'Нам нужны ваши реквизиты, чтобы...',
            'inn': '000000',
            'required': False,
        },
        'bank_ui': {
            'account_hint': '00000 00000 00000 00000',
            'account_mask': '[00000] [00000] [00000] [00000]',
            'banks': [],
            'bik_hint': '000000000',
            'bik_mask': '[000000000]',
        },
        'sbp_ui': {
            'enabled': sbp_enabled,
            'banks': [{'id': 'test_bank', 'name': 'Test Bank'}],
        },
        'data': {
            'status': 'in_progress',
            'requisites': (
                {**requisites, 'bank_name': 'Test Bank'}
                if requisites['type'] == 'sbp'
                else requisites
            ),
        },
    }

    assert response.status == 200

    triggers = set()
    while stq.selfemployed_fns_tag_contractor.has_calls:
        kwargs = stq.selfemployed_fns_tag_contractor.next_call()['kwargs']
        assert len(kwargs) == 3
        assert kwargs['park_id'] == 'newparkid'
        assert kwargs['contractor_id'] == 'newcontractorid'
        triggers.add(kwargs['trigger_id'])
    assert triggers == {'ownpark_requisites_set_resident'}


@pytest.mark.pgsql('selfemployed_main', files=['ownpark_metadata.sql'])
@pytest.mark.config(**CONFIG_PARAMS)
async def test_requisites_skip(se_client):
    park_id = 'parkid'
    contractor_id = 'contractorid'

    response = await se_client.post(
        '/self-employment/fns-se/v3/requisites',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={'step': 'requisites'},
    )
    assert await response.json() == {
        'next_step': 'finish',
        'step_count': 7,
        'step_index': 7,
    }
    assert response.status == 200
