import datetime

import pytest

from tests_cargo_crm import const

MANAGER_REQ_PARAMS = {'ticket_id': const.TICKET_ID, 'flow': 'phoenix'}
CREATE_BALANCE_CLIENT = 'create_balance_client'
CREATE_BALANCE_PERSON = 'create_balance_person'
CREATE_BALANCE_OFFER = 'create_balance_offer'
CREATE_BALANCE_CONTRACT_PREPAID = 'create_balance_contract_prepaid'
CREATE_BALANCE_CONTRACT_POSTPAID = 'create_balance_contract_postpaid'
PAYMENT_TYPE_PREPAID = 'prepaid'
PAYMENT_TYPE_POSTPAID = 'postpaid'
FIND_CLIENT = 'find_client'
FIND_PERSON = 'find_person'
FIND_OFFER = 'find_offer'


MANAGERS_CONFIG = {
    'rus': {'manager_uid': const.MANAGER_UID},
    'isr': {'manager_uid': const.ANOTHER_MANAGER_UID},
}

CREATE_BALANCE_PERSON_ERRORS = {
    'state': -1,
    'errors': {
        'error_list': [
            {
                'field': 'CLIENT_ID',
                'description': 'Client with ID 2025599096 not found in DB',
                'err': {
                    'msg': 'Client with ID 2025599096 not found in DB',
                    'object': None,
                    'object_id': 2025599096,
                    'wo_rollback': False,
                },
                'err_code': 30,
            },
            {
                'field': 'CLIENT_ID',
                'description': 'Client with ID 16213182 not found in DB',
                'err': {
                    'msg': 'Client with ID 16213182 not found in DB',
                    'object': None,
                    'object_id': 16213182,
                    'wo_rollback': False,
                },
                'err_code': 30,
            },
        ],
    },
}

CREATE_PERSON_ERRORS = {
    'fail_reason': {
        'code': 'simulate_error',
        'details': {
            'error_list': [
                {
                    'field': 'CLIENT_ID',
                    'description': 'Client with ID 2025599096 not found in DB',
                    'err': {
                        'msg': 'Client with ID 2025599096 not found in DB',
                        'object': None,
                        'object_id': 2025599096,
                        'wo_rollback': False,
                    },
                    'err_code': 30,
                },
                {
                    'field': 'CLIENT_ID',
                    'description': 'Client with ID 16213182 not found in DB',
                    'err': {
                        'msg': 'Client with ID 16213182 not found in DB',
                        'object': None,
                        'object_id': 16213182,
                        'wo_rollback': False,
                    },
                    'err_code': 30,
                },
            ],
        },
        'message': 'Errors in simulation of method.',
    },
}


@pytest.fixture(name='offer_forms')
def _load_offer_forms(load_json):
    return load_json('offer_forms.json')


@pytest.fixture(name='company_forms')
def _load_company_forms(load_json):
    return load_json('company_forms.json')


@pytest.fixture(name='expected_data')
def _load_expected_data(load_json):
    return load_json('expected_data.json')


@pytest.fixture(name='responses')
def _load_responses(load_json):
    return load_json('responses.json')


@pytest.fixture(name='company_pd_forms')
def _load_company_pd_forms(load_json):
    return load_json('company_pd_forms.json')


@pytest.fixture(autouse=True)
def _prepare_personal_ctx(
        personal_ctx, personal_handler_retrieve, company_pd_forms,
):
    phones = []
    emails = []
    for country in company_pd_forms:
        email_pd_id = company_pd_forms[country]['email_pd_id']  # email + '_id'
        emails.append({'id': email_pd_id, 'value': email_pd_id[:-3]})

        phone_pd_id = company_pd_forms[country]['phone_pd_id']  # phone + '_id'
        phones.append({'id': phone_pd_id, 'value': phone_pd_id[:-3]})
    personal_ctx.set_phones(phones)
    personal_ctx.set_emails(emails)


@pytest.mark.parametrize(
    ('country', 'find_client_code', 'expected_code', 'expected_json'),
    [
        pytest.param(
            'rus',
            404,
            200,
            {'billing_id': const.BILLING_CLIENT_ID},
            id='OK_rus',
        ),
        pytest.param(
            'isr',
            404,
            200,
            {'billing_id': const.BILLING_CLIENT_ID},
            id='OK_isr',
        ),
        # pytest.param(
        #     'rus',
        #     200,
        #     409,
        #     {
        #         'code': 'conflict',
        #         'message': 'A conflict occured.',
        #         'details': {},
        #     },
        #     id='client_exists',
        # ),
    ],
)
async def test_create_balance_client(
        taxi_cargo_crm,
        mocked_cargo_tasks,
        offer_forms,
        expected_data,
        responses,
        company_forms,
        company_pd_forms,
        find_client_code,
        expected_code,
        expected_json,
        country,
):
    mocked_cargo_tasks.upsert_client.set_response(
        200, {'client_id': const.BILLING_CLIENT_ID},
    )
    mocked_cargo_tasks.upsert_client.set_expected_data(
        expected_data[CREATE_BALANCE_CLIENT][country],
    )
    mocked_cargo_tasks.find_client.set_response(
        find_client_code, responses[FIND_CLIENT][str(find_client_code)],
    )

    request = {
        'requester_uid': const.UID,
        'robot_uid': const.ANOTHER_UID,
        'company_info_form': company_forms[country],
        'company_info_pd_form': company_pd_forms[country],
        'offer_info_form': offer_forms[country],
    }
    response = await taxi_cargo_crm.post(
        '/functions/by-flow/create-balance-client',
        params=MANAGER_REQ_PARAMS,
        json=request,
    )

    assert mocked_cargo_tasks.upsert_client_times_called == (
        1 if find_client_code == 404 else 0
    )
    assert response.status == expected_code
    assert response.json() == expected_json


async def test_procaas_stage_lock(
        taxi_cargo_crm,
        mocked_cargo_tasks,
        offer_forms,
        expected_data,
        responses,
        company_forms,
        company_pd_forms,
        find_stage_lock,
        acquire_stage_lock,
):
    country = 'rus'
    mocked_cargo_tasks.upsert_client.set_response(
        200, {'client_id': const.BILLING_CLIENT_ID},
    )
    mocked_cargo_tasks.upsert_client.set_expected_data(
        expected_data[CREATE_BALANCE_CLIENT][country],
    )
    mocked_cargo_tasks.find_client.set_response(
        404, responses[FIND_CLIENT]['404'],
    )

    request = {
        'requester_uid': const.UID,
        'robot_uid': const.ANOTHER_UID,
        'company_info_form': company_forms[country],
        'company_info_pd_form': company_pd_forms[country],
        'offer_info_form': offer_forms[country],
    }

    # test release
    response = await taxi_cargo_crm.post(
        '/functions/by-flow/create-balance-client',
        params=MANAGER_REQ_PARAMS,
        json=request,
    )
    assert find_stage_lock(const.TICKET_ID) is None

    # test already acquired
    acquire_stage_lock(const.TICKET_ID)
    response = await taxi_cargo_crm.post(
        '/functions/by-flow/create-balance-client',
        params=MANAGER_REQ_PARAMS,
        json=request,
    )
    assert mocked_cargo_tasks.upsert_client_times_called == 1
    assert response.status == 409
    assert response.json() == {
        'code': 'lock_already_acquired',
        'message': 'Lock for requested operation has already been acquired.',
        'details': {},
    }

    # test lock expired
    acquire_stage_lock(
        const.TICKET_ID,
        datetime.datetime.utcnow() - datetime.timedelta(seconds=20),
    )
    response = await taxi_cargo_crm.post(
        '/functions/by-flow/create-balance-client',
        params=MANAGER_REQ_PARAMS,
        json=request,
    )
    assert mocked_cargo_tasks.upsert_client_times_called == 2
    assert find_stage_lock(const.TICKET_ID) is None


async def test_create_association(taxi_cargo_crm, mocked_cargo_tasks):
    mocked_cargo_tasks.create_association.set_response(
        200, {'code': 0, 'message': 'OK'},
    )

    request = {
        'requester_uid': const.UID,
        'billing_id': const.BILLING_CLIENT_ID,
        'robot_uid': const.ANOTHER_UID,
    }
    response = await taxi_cargo_crm.post(
        '/functions/create-balance-association',
        params=MANAGER_REQ_PARAMS,
        json=request,
    )

    assert mocked_cargo_tasks.create_association_times_called == 1
    assert response.status == 200
    assert response.json() == {}


@pytest.mark.parametrize(
    ('country', 'is_person_exists', 'expected_code', 'expected_json'),
    [
        pytest.param(
            'rus',
            False,
            200,
            {'person_id': const.BILLING_PERSON_ID},
            id='OK_rus',
        ),
        pytest.param(
            'isr',
            False,
            200,
            {'person_id': const.BILLING_PERSON_ID},
            id='OK_isr',
        ),
        # pytest.param(
        #     'rus',
        #     True,
        #     409,
        #     {
        #         'code': 'conflict',
        #         'message': 'A conflict occured.',
        #         'details': {},
        #     },
        #     id='person_exists',
        # ),
    ],
)
async def test_create_balance_person(
        taxi_cargo_crm,
        mocked_cargo_tasks,
        offer_forms,
        expected_data,
        responses,
        company_forms,
        company_pd_forms,
        is_person_exists,
        expected_code,
        expected_json,
        country,
):
    mocked_cargo_tasks.upsert_person.set_response(
        200, {'person_id': const.BILLING_PERSON_ID},
    )
    mocked_cargo_tasks.upsert_person.set_expected_data(
        dict(
            client_id=const.BILLING_CLIENT_ID,
            **expected_data[CREATE_BALANCE_PERSON][country],
        ),
    )
    find_person_response = (
        responses[FIND_PERSON] if is_person_exists else {'persons': []}
    )
    mocked_cargo_tasks.find_person.set_response(200, find_person_response)

    request = {
        'requester_uid': const.UID,
        'billing_id': const.BILLING_CLIENT_ID,
        'company_info_form': company_forms[country],
        'company_info_pd_form': company_pd_forms[country],
        'offer_info_form': offer_forms[country],
    }
    response = await taxi_cargo_crm.post(
        '/functions/by-flow/create-balance-person',
        params=MANAGER_REQ_PARAMS,
        json=request,
    )

    assert mocked_cargo_tasks.upsert_person_times_called == (
        0 if is_person_exists else 1
    )
    assert response.status == expected_code
    assert response.json() == expected_json


@pytest.mark.config(
    CARGO_CRM_BALANCE_PERSON_CREATION_CHECK_ENABLED=True,
    CARGO_CRM_COUNTRY_SETTINGS={'rus': {'billing_id': '12345678'}},
)
@pytest.mark.parametrize(
    (
        'country',
        'is_person_exists',
        'billing_id',
        'expected_code',
        'expected_json',
        'expected_upsert_person_response',
    ),
    [
        pytest.param(
            'rus',
            False,
            const.BILLING_CLIENT_ID,
            200,
            {},
            {'state': 0, 'errors': {}},
            id='OK_rus',
        ),
        pytest.param(
            'isr',
            False,
            const.BILLING_CLIENT_ID,
            200,
            {},
            {'state': 0, 'errors': {}},
            id='OK_isr',
        ),
        # pytest.param(
        #     'rus',
        #     True,
        #     const.BILLING_CLIENT_ID,
        #     409,
        #     {
        #         'code': 'conflict',
        #         'message': 'A conflict occured.',
        #         'details': {},
        #     },
        #     {'state': 0, 'errors': {}},
        #     id='person_exists',
        # ),
        pytest.param(
            'rus',
            False,
            const.BILLING_CLIENT_ID,
            200,
            CREATE_PERSON_ERRORS,
            CREATE_BALANCE_PERSON_ERRORS,
            id='Error',
        ),
        pytest.param(
            'rus',
            False,
            '',
            200,
            {},
            {'state': 0, 'errors': {}},
            id='OK_rus without BILLING_CLIENT_ID',
        ),
    ],
)
async def test_check_can_create_balance_person(
        taxi_cargo_crm,
        mocked_cargo_tasks,
        offer_forms,
        expected_data,
        responses,
        company_forms,
        company_pd_forms,
        is_person_exists,
        billing_id,
        expected_code,
        expected_json,
        expected_upsert_person_response,
        country,
):
    mocked_cargo_tasks.upsert_person_simulate.set_response(
        200, expected_upsert_person_response,
    )
    mocked_cargo_tasks.upsert_person_simulate.set_expected_data(
        dict(
            client_id=const.BILLING_CLIENT_ID,
            **expected_data[CREATE_BALANCE_PERSON][country],
        ),
    )
    find_person_response = (
        responses[FIND_PERSON] if is_person_exists else {'persons': []}
    )
    mocked_cargo_tasks.find_person.set_response(200, find_person_response)

    request = {
        'requester_uid': const.UID,
        'billing_id': billing_id,
        'company_info_form': company_forms[country],
        'company_info_pd_form': company_pd_forms[country],
        'offer_info_form': offer_forms[country],
    }
    response = await taxi_cargo_crm.post(
        '/functions/by-flow/check-can-create-balance-person',
        params=MANAGER_REQ_PARAMS,
        json=request,
    )

    assert mocked_cargo_tasks.upsert_person_smt_times_called == (
        0 if is_person_exists else 1
    )
    assert response.status == expected_code
    assert response.json() == expected_json


@pytest.mark.parametrize(
    (
        'country',
        'expected_manager_uid',
        'managers_config',
        'expected_code',
        'expected_json',
        'is_offer_exists',
    ),
    [
        pytest.param(
            'rus',
            const.MANAGER_UID,
            MANAGERS_CONFIG.copy(),
            200,
            {
                'id': const.BILLING_OFFER_ID,
                'external_id': const.BILLING_OFFER_EXT_ID,
            },
            False,
            id='rus_OK',
        ),
        pytest.param(
            'isr',
            const.ANOTHER_MANAGER_UID,
            MANAGERS_CONFIG.copy(),
            200,
            {
                'id': const.BILLING_OFFER_ID,
                'external_id': const.BILLING_OFFER_EXT_ID,
            },
            False,
            id='isr_OK',
        ),
        pytest.param(
            'rus',
            None,
            {'isr': MANAGERS_CONFIG['isr']},
            500,
            {
                'code': 'not_found',
                'message': 'Manager UID was not found',
                'details': {},
            },
            False,
            id='no_managers',
        ),
        # pytest.param(
        #     'rus',
        #     const.ANOTHER_MANAGER_UID,
        #     MANAGERS_CONFIG.copy(),
        #     409,
        #     {
        #         'code': 'conflict',
        #         'message': 'A conflict occured.',
        #         'details': {},
        #     },
        #     True,
        #     id='offer_exists',
        # ),
    ],
)
@pytest.mark.config(
    CORP_CARGO_OFFER_ACCEPT_TERMS={
        'rus': {
            'offer_activation_payment_amount': '1000.00',
            'offer_confirmation_type': 'min-payment',
            'offer_activation_due_term': 30,
        },
        'isr': {'offer_confirmation_type': 'no'},
    },
)
async def test_create_balance_offer(
        taxi_cargo_crm,
        taxi_config,
        mocked_cargo_tasks,
        offer_forms,
        expected_data,
        responses,
        company_forms,
        expected_manager_uid,
        managers_config,
        expected_code,
        expected_json,
        is_offer_exists,
        country,
):
    taxi_config.set_values(
        {'CORP_CARGO_OFFER_BALANCE_MANAGER_UIDS': managers_config},
    )
    mocked_cargo_tasks.create_offer.set_response(
        200,
        {
            'id': const.BILLING_OFFER_ID,
            'external_id': const.BILLING_OFFER_EXT_ID,
        },
    )
    mocked_cargo_tasks.create_offer.set_expected_data(
        dict(
            client_id=const.BILLING_CLIENT_ID,
            person_id=const.BILLING_PERSON_ID,
            manager_uid=expected_manager_uid,
            **expected_data[CREATE_BALANCE_OFFER][country],
        ),
    )
    find_offer_response = (
        responses[FIND_OFFER] if is_offer_exists else {'contracts': []}
    )
    mocked_cargo_tasks.find_offer.set_response(200, find_offer_response)

    request = {
        'requester_uid': const.UID,
        'billing_id': const.BILLING_CLIENT_ID,
        'person_id': const.BILLING_PERSON_ID,
        'country': country,
        'contract_traits': {'kind': 'offer', 'payment_type': 'prepaid'},
    }
    response = await taxi_cargo_crm.post(
        '/functions/create-balance-offer',
        params=MANAGER_REQ_PARAMS,
        json=request,
    )

    assert response.status == expected_code
    assert mocked_cargo_tasks.create_offer_times_called == (
        0 if is_offer_exists or expected_code == 500 else 1
    )
    assert response.json() == expected_json


@pytest.mark.parametrize(
    (
        'country',
        'expected_manager_uid',
        'create_balance_contract',
        'payment_type',
        'expected_code',
        'expected_json',
    ),
    [
        pytest.param(
            'rus',
            const.MANAGER_UID,
            CREATE_BALANCE_CONTRACT_PREPAID,
            PAYMENT_TYPE_PREPAID,
            200,
            {
                'id': const.BILLING_CONTRACT_ID,
                'external_id': const.BILLING_CONTRACT_EXT_ID,
            },
            id='rus_prepaid_OK',
        ),
        pytest.param(
            'isr',
            const.ANOTHER_MANAGER_UID,
            CREATE_BALANCE_CONTRACT_PREPAID,
            PAYMENT_TYPE_PREPAID,
            200,
            {
                'id': const.BILLING_CONTRACT_ID,
                'external_id': const.BILLING_CONTRACT_EXT_ID,
            },
            id='isr_prepaid_OK',
        ),
        pytest.param(
            'rus',
            const.MANAGER_UID,
            CREATE_BALANCE_CONTRACT_POSTPAID,
            PAYMENT_TYPE_POSTPAID,
            200,
            {
                'id': const.BILLING_CONTRACT_ID,
                'external_id': const.BILLING_CONTRACT_EXT_ID,
            },
            id='rus_postpaid_OK',
        ),
        pytest.param(
            'isr',
            const.ANOTHER_MANAGER_UID,
            CREATE_BALANCE_CONTRACT_POSTPAID,
            PAYMENT_TYPE_POSTPAID,
            200,
            {
                'id': const.BILLING_CONTRACT_ID,
                'external_id': const.BILLING_CONTRACT_EXT_ID,
            },
            id='isr_postpaid_OK',
        ),
    ],
)
@pytest.mark.config(CORP_CARGO_OFFER_BALANCE_MANAGER_UIDS=MANAGERS_CONFIG)
async def test_create_balance_contract(
        taxi_cargo_crm,
        mocked_cargo_tasks,
        expected_data,
        expected_manager_uid,
        create_balance_contract,
        payment_type,
        expected_code,
        expected_json,
        country,
):
    mocked_cargo_tasks.create_contract.set_response(
        200,
        {
            'id': const.BILLING_CONTRACT_ID,
            'external_id': const.BILLING_CONTRACT_EXT_ID,
        },
    )
    mocked_cargo_tasks.create_contract.set_expected_data(
        dict(
            client_id=const.BILLING_CLIENT_ID,
            person_id=const.BILLING_PERSON_ID,
            manager_uid=expected_manager_uid,
            **expected_data[create_balance_contract][country],
        ),
    )

    mocked_cargo_tasks.find_offer.set_response(200, {'contracts': []})

    request = {
        'requester_uid': const.UID,
        'billing_id': const.BILLING_CLIENT_ID,
        'person_id': const.BILLING_PERSON_ID,
        'country': country,
        'contract_traits': {'kind': 'contract', 'payment_type': payment_type},
    }
    response = await taxi_cargo_crm.post(
        '/functions/create-balance-contract',
        params={'ticket_id': const.TICKET_ID},
        json=request,
    )

    assert response.status == expected_code
    assert response.json() == expected_json
