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
                    True, 'PHONE_PD_ID', True, True,
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
                    True, 'PHONE_PD_ID', True, True,
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
                    True, 'PHONE_PD_ID', True, True,
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
                    True, 'PHONE_PD_ID', True, True,
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
                    True, 'PHONE_PD_ID', True, True,
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
                    True, 'PHONE_PD_ID', True, True,
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
                    True, 'PHONE_PD_ID', False, True,
                ),
            ),
        ),
    ],
)
async def test_post_requisites_invalid(
        se_client, mock_salesforce, requisites, expected_code, expected_json,
):
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
        '/driver/v2/selfemployed/ownpark/management/requisites',
        headers=HEADERS,
        json={'requisites': requisites},
    )
    assert await response.json() == expected_json

    assert response.status == expected_code


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.config(**CONFIG_PARAMS)
@pytest.mark.parametrize(
    'requisites,sbp_enabled,expected_status',
    [
        pytest.param(
            dict(type='bank', account='40817312312312312312', bik='043123123'),
            True,
            'in_progress',
            marks=[
                pytest.mark.client_experiments3(
                    **_make_test_requested_exp_params(
                        True, 'PHONE_PD_ID', True, True,
                    ),
                ),
                pytest.mark.pgsql(
                    'selfemployed_main', files=['ownpark_metadata.sql'],
                ),
            ],
        ),  # Regular bank account, regv2
        pytest.param(
            dict(type='bank', account='40817312312312312312', bik='043123123'),
            False,
            'in_progress',
            marks=[
                pytest.mark.client_experiments3(
                    **_make_test_requested_exp_params(
                        True, 'PHONE_PD_ID', False, True,
                    ),
                ),
                pytest.mark.pgsql(
                    'selfemployed_main', files=['ownpark_metadata.sql'],
                ),
            ],
        ),  # Regular bank account, SBP disabled, regv2
        pytest.param(
            dict(type='bank', account='40820312312312312312', bik='040000000'),
            True,
            'in_progress',
            marks=[
                pytest.mark.client_experiments3(
                    **_make_test_requested_exp_params(
                        True, 'PHONE_PD_ID', True, True,
                    ),
                ),
                pytest.mark.pgsql(
                    'selfemployed_main', files=['ownpark_metadata.sql'],
                ),
            ],
        ),  # Nonresident bank account, regv2
        pytest.param(
            dict(type='sbp', phone='71231231231', bank_id='test_bank'),
            True,
            'in_progress',
            marks=[
                pytest.mark.client_experiments3(
                    **_make_test_requested_exp_params(
                        True, 'PHONE_PD_ID', True, True,
                    ),
                ),
                pytest.mark.pgsql(
                    'selfemployed_main', files=['ownpark_metadata.sql'],
                ),
            ],
        ),  # SBP account, regv2
        pytest.param(
            dict(type='bank', account='40817312312312312312', bik='043123123'),
            True,
            'in_progress',
            marks=[
                pytest.mark.client_experiments3(
                    **_make_test_requested_exp_params(
                        True, 'PHONE_PD_ID', True, True,
                    ),
                ),
                pytest.mark.pgsql(
                    'selfemployed_main', files=['dbmain_profiles.sql'],
                ),
            ],
        ),  # Regular bank account, old db
        pytest.param(
            dict(type='bank', account='40817312312312312312', bik='043123123'),
            False,
            'in_progress',
            marks=[
                pytest.mark.client_experiments3(
                    **_make_test_requested_exp_params(
                        True, 'PHONE_PD_ID', False, True,
                    ),
                ),
                pytest.mark.pgsql(
                    'selfemployed_main', files=['dbmain_profiles.sql'],
                ),
            ],
        ),  # Regular bank account, SBP disabled, old db
        pytest.param(
            dict(type='bank', account='40820312312312312312', bik='040000000'),
            True,
            'in_progress',
            marks=[
                pytest.mark.client_experiments3(
                    **_make_test_requested_exp_params(
                        True, 'PHONE_PD_ID', True, True,
                    ),
                ),
                pytest.mark.pgsql(
                    'selfemployed_main', files=['dbmain_profiles.sql'],
                ),
            ],
        ),  # Nonresident bank account, old db
        pytest.param(
            dict(type='sbp', phone='71231231231', bank_id='test_bank'),
            True,
            'in_progress',
            marks=[
                pytest.mark.client_experiments3(
                    **_make_test_requested_exp_params(
                        True, 'PHONE_PD_ID', True, True,
                    ),
                ),
                pytest.mark.pgsql(
                    'selfemployed_main', files=['dbmain_profiles.sql'],
                ),
            ],
        ),  # SBP account, old db
    ],
)
async def test_requisites(
        se_client,
        mock_salesforce,
        mock_personal,
        requisites,
        sbp_enabled,
        expected_status,
        stq,
):
    @mock_personal('/v1/tins/retrieve')
    async def _retrieve_inn_pd(request: http.Request):
        assert request.json == {'id': 'INN_PD_ID', 'primary_replica': False}
        return {'value': '000000', 'id': 'INN_PD_ID'}

    @mock_personal('/v1/phones/store')
    async def _phones_pd(request: http.Request):
        value: str = request.json['value']
        return {'value': value, 'id': 'PHONE_PD_ID'}

    @mock_salesforce('/services/data/v46.0/sobjects/Case/')
    async def _mock_add_case(request: http.Request):
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
        '/driver/v2/selfemployed/ownpark/management/requisites',
        headers=HEADERS,
        json={'requisites': requisites},
    )
    assert response.status == 200

    response = await se_client.get(
        '/driver/v2/selfemployed/ownpark/management/requisites',
        headers=HEADERS,
    )
    content = await response.json()
    assert content == {
        'base_ui': {
            'btn_next_text': 'Отправить',
            'description': 'Нам нужны ваши реквизиты, чтобы обновить',
            'inn': '000000',
            'required': True,
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
            'status': expected_status,
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
