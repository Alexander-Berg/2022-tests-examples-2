import pytest

from testsuite.utils import http

from test_selfemployed import conftest

HEADERS = {
    'X-Request-Application-Version': '9.10',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'X-YaTaxi-Driver-Profile-Id': 'newcontractorid',
    'X-YaTaxi-Park-Id': 'newparkid',
    'User-Agent': (
        'app:pro brand:yandex version:10.12 '
        'platform:ios platform_version:15.0.1'
    ),
}
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
            'banks': [{'id': 'test_bank', 'name': 'Test Bank'}],
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
        '/driver/v1/selfemployed/ownpark/management/requisites',
        headers=HEADERS,
        json={
            'personal_account': requisites['account'],
            'bik': requisites['bik'],
        },
    )
    assert await response.json() == expected_json

    assert response.status == expected_code


@pytest.mark.pgsql('selfemployed_main', files=['ownpark_metadata.sql'])
@pytest.mark.config(**CONFIG_PARAMS)
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
async def test_requisites(
        se_client, mock_salesforce, mock_personal, requisites, stq,
):
    @mock_personal('/v1/tins/retrieve')
    async def _retrieve_inn_pd(request: http.Request):
        assert request.json == {'id': 'INN_PD_ID', 'primary_replica': False}
        return {'value': '000000', 'id': 'INN_PD_ID'}

    @mock_salesforce('/services/data/v46.0/sobjects/Case/')
    async def _mock_add_case(request: http.Request):
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
        '/driver/v1/selfemployed/ownpark/management/requisites',
        headers=HEADERS,
        json={
            'personal_account': requisites['account'],
            'bik': requisites['bik'],
        },
    )
    assert response.status == 200

    response = await se_client.get(
        '/driver/v1/selfemployed/ownpark/management/requisites',
        headers=HEADERS,
    )
    content = await response.json()
    assert content == {
        'btn_next_text': 'requisites_screen_update_button_text',
        'description': 'requisites_screen_update_description',
        'required': True,
        'account_hint': '00000 00000 00000 00000',
        'account_mask': '[00000] [00000] [00000] [00000]',
        'banks': [],
        'bik_hint': '000000000',
        'bik_mask': '[000000000]',
        'inn': '000000',
        'bik': requisites['bik'],
        'account': requisites['account'],
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


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql('selfemployed_main', files=['dbmain_profiles.sql'])
async def test_requisites_old_db(
        patch, se_client, mock_personal, mock_salesforce, stq,
):
    requisites = dict(
        type='bank', account='40817312312312312312', bik='043123123',
    )

    @mock_personal('/v1/phones/store')
    async def _phones_pd(request: http.Request):
        value: str = request.json['value']
        return {'value': value, 'id': 'PHONE_PD_ID'}

    @mock_salesforce('/services/data/v46.0/sobjects/Account/AccountId')
    async def _mock_get_account(request: http.Request):
        assert request.query == {'fields': 'Type,City__c,IBAN__c,SWIFT__c'}
        return {
            'Type': 'Selfemployed',
            'City__c': 'Москва',
            'IBAN__c': requisites['account'],
            'SWIFT__c': requisites['bik'],
        }

    @mock_salesforce('/services/data/v46.0/sobjects/Case/')
    async def _mock_add_case(request: http.Request):
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

    response = await se_client.post(
        '/driver/v1/selfemployed/ownpark/management/requisites',
        headers=HEADERS,
        json={
            'personal_account': requisites['account'],
            'bik': requisites['bik'],
        },
    )
    assert response.status == 200

    response = await se_client.get(
        '/driver/v1/selfemployed/ownpark/management/requisites',
        headers=HEADERS,
    )
    content = await response.json()
    assert content == {
        'btn_next_text': 'Отправить',
        'description': 'Нам нужны ваши реквизиты, чтобы обновить',
        'required': True,
        'account_hint': '00000 00000 00000 00000',
        'account_mask': '[00000] [00000] [00000] [00000]',
        'banks': [],
        'bik_hint': '000000000',
        'bik_mask': '[000000000]',
        'inn': '000000',
        'bik': requisites['bik'],
        'account': requisites['account'],
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
