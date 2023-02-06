# pylint: disable=redefined-outer-name

import pytest

from taxi.clients import billing_v2

from corp_requests import settings
from corp_requests.internal import smart_task
from corp_requests.stq import corp_accept_manager_request

CORP_FERNET_SECRET_KEYS = (
    'zbCLq520w21vF3JLsBX2owdS6w8P752nKZzWYABe7Ns=;'
    'xqt7uUt0Nf3qTEJnqyF_9GTHOhyTIqE0-XDk7fBlVfI='
)

CORP_FEATURE_SETTINGS = [
    {
        'country': 'rus',
        'feature_groups': [
            {
                'name': '__default__',
                'features': [
                    {'name': 'api_allowed'},
                    {'name': 'combo_orders_allowed'},
                    {'name': 'new_limits'},
                ],
            },
            {'name': 'without_vat', 'features': [{'name': 'new_limits'}]},
        ],
    },
    {
        'country': 'blr',
        'feature_groups': [
            {
                'name': '__default__',
                'features': [
                    {'name': 'api_allowed'},
                    {'name': 'combo_orders_allowed'},
                    {'name': 'new_limits'},
                ],
            },
        ],
    },
    {
        'country': 'kaz',
        'feature_groups': [
            {
                'name': '__default__',
                'features': [
                    {'name': 'api_allowed'},
                    {'name': 'combo_orders_allowed'},
                    {'name': 'new_limits'},
                ],
            },
        ],
    },
    {
        'country': 'kgz',
        'feature_groups': [
            {
                'name': '__default__',
                'features': [
                    {'name': 'api_allowed'},
                    {'name': 'combo_orders_allowed'},
                    {'name': 'new_limits'},
                ],
            },
        ],
    },
]

DEFAULT_FEATURES = ['api_allowed', 'combo_orders_allowed', 'new_limits']

DEFAULT_EXPECTED_RESULT = {
    'bank_account_number': 'bank_account_number',
    'bank_bic': 'bank_bic',
    'billing_client_id': 1,
    'billing_contract_id': 2,
    'billing_external_id': 'external_id',
    'billing_person_id': 3,
    'client_id': 'client_id',
    'client_login_id': 'new_login_id',
    'client_tmp_password': 'P@ssw0rd',
    'company_tin_id': 'tin_pd_id',
    'contacts': [
        {
            'email_id': 'example@yandex.ru_id',
            'name': 'name',
            'phone_id': 'phone_pd_id_1',
        },
    ],
    'contract_type': 'postpaid',
    'enterprise_name_full': 'ОБЩЕСТВО Ромашка 23',
    'enterprise_name_short': 'ООО Ромашка 23',
    'legal_address': '19995;legal_address',
    'mailing_address': '19995;mailing_address',
    'manager_login': 'manager_login',
    'signer_duly_authorized': 'charter',
    'signer_gender': 'male',
    'signer_name': 'signer_name',
    'signer_position': 'signer_position',
    'status': 'accepted',
    'step': 9,
    'locked_fields': [
        'enterprise_name_short',
        'contacts',
        'billing_client_id',
        'company_tin',
        'bank_bic',
        'enterprise_name_full',
        'mailing_postcode',
        'mailing_address',
        'legal_postcode',
        'legal_address',
        'signer_name',
        'signer_gender',
        'signer_position',
        'company_cio',
        'bank_account_number',
        'billing_person_id',
        'contract_type',
        'service',
        'desired_button_name',
        'client_id',
        'reason',
    ],
}

CREATE_PERSON_MSG = (
    'Error during call to billing: <error><msg>Missing '
    'mandatory person field "kpp" for person type ur</msg>'
    '<field>kpp</field><wo-rollback>0</wo-rollback>'
    '<person-type>ur</person-type><method>'
    'Balance2.CreatePerson</method><code>'
    'MISSING_MANDATORY_PERSON_FIELD</code><parent-codes>'
    '<code>INVALID_PARAM</code><code>EXCEPTION</code>'
    '</parent-codes><contents>Missing mandatory person '
    'field "kpp" for person type ur</contents></error>'
)


@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}])
async def test_init_task_failed(stq3_context, patch, db):
    @patch('corp_requests.stq.corp_accept_manager_request.BaseTask.run')
    async def _task_run():
        raise smart_task.SmartTaskError

    await corp_accept_manager_request.task(
        stq3_context,
        {
            '_id': 'minimal',
            'contacts': [],
            'legal_address': '19995;legal_address',
            'mailing_address': '19995;mailing_postcode',
        },
        operator_uid='',
        operator_login='',
        user_ip='',
    )
    doc = await db.corp_manager_requests.find_one({'_id': 'minimal'})
    assert doc['status'] == 'failed'


CORP_OFFER_BALANCE_MANAGER_UIDS = {
    'rus': {'__default__': [123, 456, 789], 'cargo': [234, 567, 890]},
    'blr': {'__default__': [123, 456, 789], 'cargo': [234, 567, 890]},
    'kaz': {'__default__': [123, 456, 789], 'cargo': [234, 567, 890]},
    'kgz': {'__default__': [123, 456, 789], 'cargo': [234, 567, 890]},
}


@pytest.fixture
def mass_mock(
        patch,
        mock_corp_clients,
        mock_mds,
        mock_personal,
        mock_corp_admin,
        mock_staff,
        mock_sender,
):
    @patch('taxi.clients.billing_v2.BalanceClient.get_passport_by_login')
    async def _get_passport_by_login(*args, **kwargs):
        return {'Uid': '42'}

    @patch('taxi.clients.billing_v2.BalanceClient.create_client')
    async def _create_billing_client(*args, **kwargs):
        return 1

    @patch(
        'taxi.clients.billing_v2.BalanceClient.create_user_client_association',
    )
    async def _create_user_client_association(*args, **kwargs):
        pass

    @patch('taxi.clients.billing_v2.BalanceClient.create_person')
    async def _create_person(*args, **kwargs):
        return 3

    @patch('taxi.clients.billing_v2.BalanceClient.create_common_contract')
    async def _create_common_contract(*args, **kwargs):
        return {'ID': 2, 'EXTERNAL_ID': 'external_id'}


@pytest.mark.config(
    CORP_OFFER_BALANCE_MANAGER_UIDS=CORP_OFFER_BALANCE_MANAGER_UIDS,
    CORP_MANAGER_REQUEST_CHANGE_STATUS_SLUG_SERVICES={
        '__default__': 'SLUG',
        'cargo': 'cargoSLUG',
    },
    CORP_FEATURES_SETTINGS=CORP_FEATURE_SETTINGS,
    TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}],
)
@pytest.mark.parametrize(
    'request_id, expected_doc',
    [
        ('minimal', dict(DEFAULT_EXPECTED_RESULT, _id='minimal')),
        ('multi', dict(DEFAULT_EXPECTED_RESULT, _id='multi', service='multi')),
        ('cargo', dict(DEFAULT_EXPECTED_RESULT, _id='cargo', service='cargo')),
        ('eats2', dict(DEFAULT_EXPECTED_RESULT, _id='eats2', service='eats2')),
        (
            'maximal',
            {
                '_id': 'maximal',
                'country': 'kaz',
                'city': 'мск',
                'kbe': '11',
                'bank_account_number': 'bank_account_number',
                'bank_bic': 'bank_bic',
                'billing_client_id': 1,
                'billing_contract_id': 2,
                'billing_external_id': 'external_id',
                'billing_person_id': 3,
                'client_id': 'client_id',
                'client_login_id': 'new_login_id',
                'client_tmp_password': 'P@ssw0rd',
                'company_tin_id': 'tin_pd_id',
                'company_cin': 'company_cin',
                'contacts': [
                    {
                        'email_id': 'example@yandex.ru_id',
                        'name': 'name',
                        'phone_id': 'phone_pd_id_1',
                    },
                    {'name': 'name', 'phone_id': 'phone_pd_id_1'},
                ],
                'contract_type': 'postpaid',
                'enterprise_name_full': 'ОБЩЕСТВО Ромашка 23',
                'enterprise_name_short': 'ООО Ромашка 23',
                'legal_address': '19995;legal_address',
                'mailing_address': '19995;mailing_address',
                'manager_login': 'manager_login',
                'attachments': [
                    {'filename': 'filename1', 'file_key': 'file_key1'},
                    {'filename': 'filename2', 'file_key': 'file_key2'},
                ],
                'signer_duly_authorized': 'authority_agreement',
                'signer_gender': 'male',
                'signer_name': 'signer_name',
                'signer_position': 'signer_position',
                'st_link': 'st_link',
                'desired_button_name': 'Ромашка',
                'status': 'accepted',
                'service': 'hard_delivery',
                'step': 9,
                'locked_fields': [
                    'enterprise_name_short',
                    'contacts',
                    'billing_client_id',
                    'company_tin',
                    'bank_bic',
                    'enterprise_name_full',
                    'mailing_postcode',
                    'mailing_address',
                    'legal_postcode',
                    'legal_address',
                    'signer_name',
                    'signer_gender',
                    'signer_position',
                    'bank_account_number',
                    'city',
                    'kbe',
                    'bank_name',
                    'billing_person_id',
                    'contract_type',
                    'service',
                    'desired_button_name',
                    'client_id',
                    'reason',
                ],
            },
        ),
        (
            'belarus',
            {
                '_id': 'belarus',
                'bank_account_number': 'bank_account_number',
                'bank_bic': 'bank_bic',
                'city': 'Минск',
                'company_cin': 'company_cin',
                'company_tin_id': 'tin_pd_id',
                'contacts': [
                    {
                        'email_id': 'example@yandex.ru_id',
                        'name': 'name',
                        'phone_id': 'phone_pd_id_1',
                    },
                    {'name': 'name', 'phone_id': 'phone_pd_id_1'},
                ],
                'contract_type': 'postpaid',
                'country': 'blr',
                'desired_button_name': 'Ромашка',
                'enterprise_name_full': 'ОБЩЕСТВО Ромашка 23',
                'enterprise_name_short': 'ООО Ромашка 23',
                'legal_address': '19995;legal_address',
                'mailing_address': '19995;mailing_address',
                'manager_login': 'manager_login',
                'service': 'hard_delivery',
                'signer_duly_authorized': 'authority_agreement',
                'signer_gender': 'male',
                'signer_name': 'signer_name',
                'signer_position': 'signer_position',
                'st_link': 'st_link',
                'client_login_id': 'new_login_id',
                'client_tmp_password': 'P@ssw0rd',
                'billing_client_id': 1,
                'billing_person_id': 3,
                'billing_contract_id': 2,
                'billing_external_id': 'external_id',
                'client_id': 'client_id',
                'status': 'accepted',
                'step': 9,
                'locked_fields': [
                    'enterprise_name_short',
                    'contacts',
                    'billing_client_id',
                    'company_tin',
                    'bank_bic',
                    'enterprise_name_full',
                    'mailing_postcode',
                    'mailing_address',
                    'legal_postcode',
                    'legal_address',
                    'signer_name',
                    'signer_gender',
                    'signer_position',
                    'bank_account_number',
                    'city',
                    'bank_name',
                    'billing_person_id',
                    'contract_type',
                    'service',
                    'desired_button_name',
                    'client_id',
                    'reason',
                ],
            },
        ),
        (
            'cargo_belarus',
            {
                '_id': 'cargo_belarus',
                'bank_account_number': 'bank_account_number',
                'bank_bic': 'bank_bic',
                'bank_name': 'cargo_blr_bank',
                'city': 'Минск',
                'company_tin_id': 'tin_pd_id',
                'contacts': [
                    {
                        'email_id': 'example@yandex.ru_id',
                        'name': 'name',
                        'phone_id': 'phone_pd_id_1',
                    },
                    {'name': 'name', 'phone_id': 'phone_pd_id_1'},
                ],
                'contract_type': 'postpaid',
                'country': 'blr',
                'desired_button_name': 'Ромашка',
                'enterprise_name_full': 'ОБЩЕСТВО Ромашка 23',
                'enterprise_name_short': 'ООО Ромашка 23',
                'legal_address': '19995;legal_address',
                'mailing_address': '19995;mailing_address',
                'manager_login': 'blr_manager_login',
                'service': 'cargo',
                'signer_duly_authorized': 'authority_agreement',
                'signer_gender': 'male',
                'signer_name': 'signer_name',
                'signer_position': 'signer_position',
                'st_link': 'st_link',
                'client_login_id': 'new_login_id',
                'client_tmp_password': 'P@ssw0rd',
                'billing_client_id': 1,
                'billing_person_id': 3,
                'billing_contract_id': 2,
                'billing_external_id': 'external_id',
                'client_id': 'client_id',
                'status': 'accepted',
                'step': 9,
                'locked_fields': [
                    'enterprise_name_short',
                    'contacts',
                    'billing_client_id',
                    'company_tin',
                    'bank_bic',
                    'enterprise_name_full',
                    'mailing_postcode',
                    'mailing_address',
                    'legal_postcode',
                    'legal_address',
                    'signer_name',
                    'signer_gender',
                    'signer_position',
                    'bank_account_number',
                    'city',
                    'bank_name',
                    'billing_person_id',
                    'contract_type',
                    'service',
                    'desired_button_name',
                    'client_id',
                    'reason',
                ],
            },
        ),
        (
            'kgz',
            {
                '_id': 'kgz',
                'bank_account_number': 'bank_account_number',
                'bank_bic': 'bank_bic',
                'bank_swift': 'bank_swift',
                'registration_number': '123456-1234-ООО',
                'city': 'Бишкек',
                'company_cin': 'company_cin',
                'company_tin_id': 'tin_pd_id',
                'contacts': [
                    {
                        'email_id': 'example@yandex.ru_id',
                        'name': 'name',
                        'phone_id': 'phone_pd_id_1',
                    },
                    {'name': 'name', 'phone_id': 'phone_pd_id_1'},
                ],
                'contract_type': 'postpaid',
                'country': 'kgz',
                'desired_button_name': 'Ромашка',
                'enterprise_name_full': 'ОБЩЕСТВО Ромашка 23',
                'enterprise_name_short': 'ООО Ромашка 23',
                'legal_address': '19995;legal_address',
                'mailing_address': '19995;mailing_address',
                'manager_login': 'manager_login',
                'service': 'hard_delivery',
                'signer_duly_authorized': 'authority_agreement',
                'signer_gender': 'male',
                'signer_name': 'signer_name',
                'signer_position': 'signer_position',
                'st_link': 'st_link',
                'client_login_id': 'new_login_id',
                'client_tmp_password': 'P@ssw0rd',
                'billing_client_id': 1,
                'billing_person_id': 3,
                'billing_contract_id': 2,
                'billing_external_id': 'external_id',
                'client_id': 'client_id',
                'status': 'accepted',
                'step': 9,
                'locked_fields': [
                    'enterprise_name_short',
                    'contacts',
                    'billing_client_id',
                    'company_tin',
                    'bank_bic',
                    'enterprise_name_full',
                    'mailing_postcode',
                    'mailing_address',
                    'legal_postcode',
                    'legal_address',
                    'signer_name',
                    'signer_gender',
                    'signer_position',
                    'bank_account_number',
                    'city',
                    'bank_name',
                    'bank_swift',
                    'registration_number',
                    'billing_person_id',
                    'contract_type',
                    'service',
                    'desired_button_name',
                    'client_id',
                    'reason',
                ],
            },
        ),
    ],
)
async def test_task_run(
        stq3_context,
        stq,
        mock_corp_clients,
        mass_mock,
        patch,
        db,
        expected_doc,
        request_id,
        mockserver,
):
    secdist = stq3_context.secdist['settings_override']
    secdist['CORP_FERNET_SECRET_KEYS'] = CORP_FERNET_SECRET_KEYS

    logger_info = corp_accept_manager_request.logger.info

    @patch('corp_requests.internal.smart_task.logger.info')
    def _info_log(*args, **kwargs):
        logger_info(*args, **kwargs)

    doc = await db.corp_manager_requests.find_one({'_id': request_id})
    old_updated = doc['updated']
    await corp_accept_manager_request.task(
        stq3_context, doc, operator_uid='', operator_login='', user_ip='',
    )

    doc = await db.corp_manager_requests.find_one({'_id': request_id})
    assert doc['updated'] != old_updated
    old_updated = doc.pop('updated')
    doc.pop('created', None)
    doc.pop('tasks', None)
    doc.pop('final_status_date', None)

    # decrypt password
    doc['client_tmp_password'] = stq3_context.corp_crypto.decrypt(
        doc['client_tmp_password'],
    )

    assert doc == expected_doc

    # check create client mock
    create_client_call = mock_corp_clients.create_client.next_call()
    name = expected_doc.get('desired_button_name', '').strip()
    if not name:
        name = expected_doc['enterprise_name_short']
    data = {
        'name': name,
        'country': expected_doc.get('country', 'rus'),
        'email': 'example@yandex.ru',
        'features': DEFAULT_FEATURES,
        'yandex_login': 'new_login',
    }
    if 'city' in doc:
        data['city'] = doc['city']
    assert create_client_call['request'].json == data
    assert not mock_corp_clients.create_client.has_calls

    # check activated services
    mocks = {
        'taxi': mock_corp_clients.service_taxi,
        'cargo': mock_corp_clients.service_cargo,
        'drive': mock_corp_clients.service_drive,
        'eats2': mock_corp_clients.service_eats2,
    }
    services_to_activate = settings.OFFER_NAMES_BY_COUNTRY[
        doc.get('country', 'rus')
    ].get(doc['contract_type'], [])
    for service, mock in mocks.items():
        if service in services_to_activate:
            data = {'is_active': True, 'is_visible': True}
            call = mock.next_call()
            assert call['request'].json == data

    assert [call['args'] for call in _info_log.calls] == [
        ('Done step %s, function %s', 0, 'create_passport_account'),
        ('Done step %s, function %s', 1, 'create_billing_client'),
        ('Done step %s, function %s', 2, 'create_billing_association'),
        ('Done step %s, function %s', 3, 'create_billing_person'),
        ('Done step %s, function %s', 4, 'create_billing_contract'),
        ('Done step %s, function %s', 5, 'create_client'),
        ('Done step %s, function %s', 6, 'activate_services'),
        ('Done step %s, function %s', 7, 'notify_docs'),
        ('Done step %s, function %s', 8, 'run_sync_stq'),
    ]

    await corp_accept_manager_request.task(
        stq3_context, doc, operator_uid='', operator_login='', user_ip='',
    )

    doc = await db.corp_manager_requests.find_one({'_id': request_id})
    assert doc.pop('updated') == old_updated
    doc.pop('created', None)
    doc.pop('tasks', None)
    doc.pop('final_status_date', None)

    # decrypt password
    doc['client_tmp_password'] = stq3_context.corp_crypto.decrypt(
        doc['client_tmp_password'],
    )

    assert doc == expected_doc
    assert [call['args'] for call in _info_log.calls] == [
        ('Skipped step %s, function %s', 0, 'create_passport_account'),
        ('Skipped step %s, function %s', 1, 'create_billing_client'),
        ('Skipped step %s, function %s', 2, 'create_billing_association'),
        ('Skipped step %s, function %s', 3, 'create_billing_person'),
        ('Skipped step %s, function %s', 4, 'create_billing_contract'),
        ('Skipped step %s, function %s', 5, 'create_client'),
        ('Skipped step %s, function %s', 6, 'activate_services'),
        ('Skipped step %s, function %s', 7, 'notify_docs'),
        ('Skipped step %s, function %s', 8, 'run_sync_stq'),
    ]

    # check stq calls

    assert stq.corp_notices_process_event.times_called == 1
    assert stq.corp_notices_process_event.next_call()['kwargs'] == {
        'event_name': 'ManagerRequestStatusChanged',
        'data': {
            'request_id': request_id,
            'old': {'status': 'pending'},
            'new': {'status': 'accepted'},
        },
    }

    assert stq.corp_sync_client_info.times_called == 1
    assert stq.corp_sync_client_info.next_call()['kwargs'] == {
        'client_id': 'client_id',
        'billing_client_id': '1',
    }
    assert stq.corp_sync_contracts_info.times_called == 1
    assert stq.corp_sync_contracts_info.next_call()['kwargs'] == {
        'client_id': 'client_id',
        'billing_client_id': '1',
    }


@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}])
async def test_task_run_error(stq3_context, mass_mock, patch, db):

    secdist = stq3_context.secdist['settings_override']
    secdist['CORP_FERNET_SECRET_KEYS'] = CORP_FERNET_SECRET_KEYS

    @patch('taxi.clients.billing_v2.BalanceClient.create_person')
    async def _create_person(*args, **kwargs):
        raise billing_v2.BillingError(CREATE_PERSON_MSG)

    request_id = 'maximal'
    doc = await db.corp_manager_requests.find_one({'_id': request_id})
    await corp_accept_manager_request.task(
        stq3_context, doc, operator_uid='', operator_login='', user_ip='',
    )

    doc = await db.corp_manager_requests.find_one({'_id': request_id})
    assert doc['last_error'] == 'error.person_creation_error'
