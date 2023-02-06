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


@pytest.mark.pgsql('selfemployed_main', files=['ownpark_metadata.sql'])
@pytest.mark.config(**CONFIG_PARAMS)
@pytest.mark.parametrize(
    'requisites,expected_code,expected_json',
    [
        pytest.param(
            {'account': '40817312312312312312', 'bik': '1231'},
            409,
            {'bik_error': 'error_incorrect_bik'},
        ),
        pytest.param(
            {'account': '40817312312312312312', 'bik': '123123123'},
            409,
            {'bik_error': 'error_incorrect_bik'},
        ),
        pytest.param(
            {'account': '40820312312312312312', 'bik': '043123123'},
            409,
            {
                'bik_error': 'error_bank_not_eligible_for_nonresident',
                'nonresident_bank_error': {
                    'button_text': 'error_bank_not_eligible_button_text',
                    'subtitle': 'error_bank_not_eligible_subtitle',
                    'title': 'error_bank_not_eligible_title',
                },
            },
        ),
        pytest.param(
            {'account': '1231', 'bik': '043123123'},
            409,
            {'account_error': 'error_incorrect_account_format'},
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
        return {
            'Type': 'Selfemployed',
            'City__c': 'Москва',
            'IBAN__c': requisites['account'],
            'SWIFT__c': requisites['bik'],
        }

    response = await se_client.post(
        '/self-employment/fns-se/v2/requisites',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={
            'step': 'requisites',
            'personal_account': requisites['account'],
            'bik': requisites['bik'],
        },
    )
    assert await response.json() == expected_json

    assert response.status == expected_code


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql('selfemployed_main', files=['ownpark_metadata.sql'])
@pytest.mark.parametrize(
    'requisites',
    [
        dict(
            account='40817312312312312312', bik='043123123',
        ),  # Regular bank account
        dict(
            account='40820312312312312312', bik='040000000',
        ),  # Nonresident bank account
    ],
)
@pytest.mark.config(**CONFIG_PARAMS)
async def test_requisites(
        se_client, mock_salesforce, mock_personal, requisites, stq,
):
    park_id = 'parkid'
    contractor_id = 'contractorid'

    @mock_personal('/v1/tins/retrieve')
    async def _retrieve_inn_pd(request: http.Request):
        assert request.json == {'id': 'INN_PD_ID', 'primary_replica': False}
        return {'value': '000000', 'id': 'INN_PD_ID'}

    @mock_salesforce('/services/data/v46.0/sobjects/Case/')
    async def _mock_add_sobject(request: http.Request):
        assert request.json == {
            'RecordTypeId': 'RecordTypeCase',
            'AccountId': 'AccountId',
            'Status': 'In Progress',
            'Origin': 'API',
            'IBAN__c': requisites['account'],
            'SWIFT__c': requisites['bik'],
            'Subject': 'Self-Employed Change Payment Details',
        }
        return {'id': 'CaseId'}

    @mock_salesforce('/services/data/v46.0/sobjects/Case/CaseId')
    async def _mock_get_case(request: http.Request):
        assert request.query == {'fields': 'IBAN__c,SWIFT__c,Subject,Status'}
        return {
            'IBAN__c': requisites['account'],
            'SWIFT__c': requisites['bik'],
            'Subject': 'Self-Employed Change Payment Details',
            'Status': 'In Progress',
        }

    @mock_salesforce('/services/data/v46.0/sobjects/Account/AccountId')
    async def _mock_get_account(request: http.Request):
        assert request.query == {'fields': 'Type,City__c,IBAN__c,SWIFT__c'}
        return {
            'Type': 'Selfemployed',
            'City__c': 'Москва',
            'IBAN__c': requisites['account'],
            'SWIFT__c': requisites['bik'],
        }

    response = await se_client.post(
        '/self-employment/fns-se/v2/requisites',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
        json={
            'step': 'requisites',
            'personal_account': requisites['account'],
            'bik': requisites['bik'],
        },
    )
    assert await response.json() == {
        'next_step': 'finish',
        'step_count': 7,
        'step_index': 7,
    }
    assert response.status == 200

    response = await se_client.get(
        '/self-employment/fns-se/v2/requisites',
        headers=conftest.DEFAULT_HEADERS,
        params={'park': park_id, 'driver': contractor_id},
    )
    content = await response.json()
    assert content == {
        'btn_next_text': 'Далее',
        'description': 'Нам нужны ваши реквизиты, чтобы...',
        'inn': '000000',
        'required': False,
        'account_hint': '00000 00000 00000 00000',
        'account_mask': '[00000] [00000] [00000] [00000]',
        'banks': [],
        'bik_hint': '000000000',
        'bik_mask': '[000000000]',
        'account': requisites['account'],
        'bik': requisites['bik'],
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
        '/self-employment/fns-se/v2/requisites',
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
