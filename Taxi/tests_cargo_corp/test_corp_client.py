import pytest  # noqa: F401

from testsuite.utils import matching

from tests_cargo_corp import utils


COMPANY_DATA = {
    'company': {
        'name': 'horns and hooves',
        'emails': [{'text': 'hornsandhooves@yandex.ru'}],
        'phones': [{'number': '+79161234567'}],
        'url': 'www.hornsandhooves.com',
        'city': 'br_moscow',
        'country': 'br_russia',
        'segment': 'Аптеки',
        'tin': '1234567890',
    },
}


@pytest.fixture(name='make_client_create_request')
def _make_client_create_request(taxi_cargo_corp):
    async def wrapper(json=None):
        response = await taxi_cargo_corp.post(
            '/internal/cargo-corp/v1/client/create',
            headers={
                'X-B2B-Client-Id': utils.CORP_CLIENT_ID_1,
                'X-Yandex-Uid': utils.YANDEX_UID,
            },
            json=json or {},
        )
        return response

    return wrapper


@pytest.fixture(name='make_client_info_request')
def _make_client_info_request(taxi_cargo_corp):
    async def wrapper(is_internal=True):
        client_info_url = '/v1/client/info'
        if is_internal:
            client_info_url = utils.INTERNAL_PREFIX + client_info_url
        response = await taxi_cargo_corp.get(
            client_info_url,
            headers={
                'X-B2B-Client-Id': utils.CORP_CLIENT_ID_1,
                'X-Yandex-Uid': utils.YANDEX_UID,
            },
        )
        return response

    return wrapper


@pytest.fixture(name='make_client_edit_request')
def _make_client_edit_request(taxi_cargo_corp):
    async def wrapper(client_id, json=None, is_internal=True):
        client_edit_url = '/v1/client/edit'
        if is_internal:
            client_edit_url = utils.INTERNAL_PREFIX + client_edit_url
        response = await taxi_cargo_corp.post(
            client_edit_url,
            headers={
                'X-B2B-Client-Id': client_id,
                'X-Yandex-Uid': utils.YANDEX_UID,
            },
            json=json or {},
        )
        return response

    return wrapper


@pytest.fixture(name='make_client_remove_request')
def _make_client_remove_request(taxi_cargo_corp):
    async def wrapper(client_id):
        response = await taxi_cargo_corp.post(
            '/internal/cargo-corp/v1/client/remove',
            headers={
                'X-B2B-Client-Id': client_id,
                'X-Yandex-Uid': utils.YANDEX_UID,
            },
        )
        return response

    return wrapper


async def prepare_billing_client(
        make_client_balance_upsert_request, billing_id, corp_client_id,
):
    request = {'billing_id': billing_id, 'contract': utils.PHOENIX_CONTRACT}
    response = await make_client_balance_upsert_request(
        corp_client_id, request,
    )
    assert response.status_code == 200


async def test_client_create(taxi_cargo_corp, make_client_create_request):
    for _ in range(2):
        response = await make_client_create_request(json=COMPANY_DATA)
        assert response.status_code == 200


async def test_client_info(
        taxi_cargo_corp,
        taxi_config,
        mocked_cargo_crm,
        make_client_balance_upsert_request,
        make_client_create_request,
        make_client_info_request,
):
    response = await make_client_create_request(json=COMPANY_DATA)
    assert response.status_code == 200

    response = await make_client_info_request(is_internal=True)
    assert response.status_code == 200
    assert response.json() == {
        'company': {
            'name': 'horns and hooves',
            'emails': [{'text': 'hornsandhooves@yandex.ru'}],
            'phones': [{'number': '+79161234567'}],
            'url': 'www.hornsandhooves.com',
            'city': 'Москва',
            'country': 'br_russia',
            'localized_country': 'Россия',
            'segment': 'Аптеки',
            'tin': '1234567890',
        },
        'corp_client_id': utils.CORP_CLIENT_ID_1,
        'revision': 1,
        'created_ts': matching.datetime_string,
        'updated_ts': matching.datetime_string,
        'payment': {'schema': {'id': 'agent', 'localized_id': 'Агентская'}},
    }

    response = await make_client_info_request(is_internal=False)
    assert response.status_code == 404


def prepare_mocks(
        mocked_cargo_crm,
        get_taxi_corp_contracts,
        has_contracts=True,
        is_active=True,
        is_sent=True,
        is_faxed=True,
        is_signed=True,
):
    mocked_cargo_crm.notification_contract_accepted.set_expected_data(
        {'corp_client_id': utils.CORP_CLIENT_ID_1},
    )
    mocked_cargo_crm.notification_contract_accepted.set_response(200, {})

    get_taxi_corp_contracts.set_contracts(
        has_contracts=has_contracts,
        is_active=is_active,
        is_sent=is_sent,
        is_faxed=is_faxed,
        is_signed=is_signed,
    )


async def create_client(make_client_create_request):
    response = await make_client_create_request(json=COMPANY_DATA)
    assert response.status_code == 200


def get_expected_contract(
        contract_activity_status='active',
        contract_progress_status='is_signed',
):
    expected_contract = {
        'external_id': '123/45',
        'activity_status': contract_activity_status,
        'progress_status': contract_progress_status,
        'contract_type': 'offer',
        'payment_type': 'prepaid',
        'created_ts': matching.datetime_string,
    }
    if contract_activity_status != 'unknown':
        expected_contract['balances'] = {'balance': '150'}
    return expected_contract


@pytest.mark.parametrize(
    'expected_contract_activity_status',
    (
        pytest.param('active'),
        pytest.param('inactive'),
        pytest.param('unknown'),
    ),
)
async def test_client_info_contract_activity_status(
        taxi_cargo_corp,
        mocked_cargo_crm,
        make_client_balance_upsert_request,
        make_client_create_request,
        make_client_info_request,
        get_taxi_corp_contracts,
        expected_contract_activity_status,
):
    prepare_mocks(
        mocked_cargo_crm=mocked_cargo_crm,
        get_taxi_corp_contracts=get_taxi_corp_contracts,
        has_contracts=expected_contract_activity_status != 'unknown',
        is_active=expected_contract_activity_status == 'active',
    )
    await create_client(make_client_create_request)
    await prepare_billing_client(
        make_client_balance_upsert_request,
        billing_id='billing_id',
        corp_client_id=utils.CORP_CLIENT_ID_1,
    )

    expected_contract = get_expected_contract(
        contract_activity_status=expected_contract_activity_status,
    )

    response = await make_client_info_request(is_internal=True)
    assert response.status_code == 200
    contract = response.json()['contract']
    assert contract['activity_status'] == expected_contract['activity_status']


@pytest.mark.parametrize(
    ('is_sent', 'is_faxed', 'is_signed', 'expected_contract_progress_status'),
    (
        pytest.param(False, False, False, 'initial'),
        pytest.param(True, False, False, 'is_sent'),
        pytest.param(True, True, False, 'is_faxed'),
        pytest.param(True, True, True, 'is_signed'),
        pytest.param(False, False, False, 'unknown'),
    ),
)
async def test_client_info_contract_progress_status(
        taxi_cargo_corp,
        mocked_cargo_crm,
        make_client_balance_upsert_request,
        make_client_create_request,
        make_client_info_request,
        get_taxi_corp_contracts,
        is_sent,
        is_faxed,
        is_signed,
        expected_contract_progress_status,
):
    prepare_mocks(
        mocked_cargo_crm=mocked_cargo_crm,
        get_taxi_corp_contracts=get_taxi_corp_contracts,
        has_contracts=expected_contract_progress_status != 'unknown',
        is_active=True,
        is_sent=is_sent,
        is_faxed=is_faxed,
        is_signed=is_signed,
    )
    await create_client(make_client_create_request)
    await prepare_billing_client(
        make_client_balance_upsert_request,
        billing_id='billing_id',
        corp_client_id=utils.CORP_CLIENT_ID_1,
    )

    expected_contract = get_expected_contract(
        contract_progress_status=expected_contract_progress_status,
    )

    response = await make_client_info_request(is_internal=True)
    assert response.status_code == 200
    contract = response.json()['contract']
    assert contract['progress_status'] == expected_contract['progress_status']


@pytest.mark.parametrize(
    (
        'is_notify_crm_contract_is_active_by_client_info_enabled',
        'contract_activity_status',
        'is_call_crm_expected',
    ),
    (
        pytest.param(False, 'active', False, id='config off'),
        pytest.param(
            True, 'active', True, id='config on && contract is active',
        ),
        pytest.param(True, 'inactive', False, id='contract is inactive'),
        pytest.param(True, 'unknown', False, id='contract is unknown'),
    ),
)
async def test_client_info_notify_crm_contract_is_active(
        taxi_cargo_corp,
        taxi_config,
        mocked_cargo_crm,
        make_client_balance_upsert_request,
        make_client_create_request,
        make_client_info_request,
        get_taxi_corp_contracts,
        is_notify_crm_contract_is_active_by_client_info_enabled,
        contract_activity_status,
        is_call_crm_expected,
):
    taxi_config.set_values(
        {
            'CARGO_CORP_ROLL_OUT_OPTIONS_ENABLED': {
                'is_notify_crm_contract_is_active_by_client_info_enabled': (
                    is_notify_crm_contract_is_active_by_client_info_enabled
                ),
            },
        },
    )
    await taxi_cargo_corp.invalidate_caches()

    prepare_mocks(
        mocked_cargo_crm=mocked_cargo_crm,
        get_taxi_corp_contracts=get_taxi_corp_contracts,
        has_contracts=contract_activity_status != 'unknown',
        is_active=contract_activity_status == 'active',
    )
    await create_client(make_client_create_request)
    await prepare_billing_client(
        make_client_balance_upsert_request,
        billing_id='billing_id',
        corp_client_id=utils.CORP_CLIENT_ID_1,
    )

    response = await make_client_info_request(is_internal=True)
    assert response.status_code == 200

    if is_call_crm_expected:
        assert (
            mocked_cargo_crm.notification_contract_accepted_times_called == 1
        )
    else:
        assert (
            mocked_cargo_crm.notification_contract_accepted_times_called == 0
        )


async def test_client_info_readable_names(
        taxi_cargo_corp, make_client_create_request, make_client_info_request,
):
    response = await make_client_create_request(json=COMPANY_DATA)
    assert response.status_code == 200

    response = await make_client_info_request(is_internal=True)
    assert response.status_code == 200
    assert response.json()['company']['city'] == 'Москва'
    assert response.json()['company']['country'] == 'br_russia'
    assert response.json()['company']['localized_country'] == 'Россия'


@pytest.mark.parametrize(
    ('cargo_corp_country_specifics', 'web_ui_languages'),
    (
        pytest.param({}, None, id='none'),
        pytest.param(
            {
                'br_russia': {
                    'languages': {
                        'default_language': {'code': 'ru'},
                        'web_ui_languages': [{'code': 'ru'}, {'code': 'en'}],
                    },
                },
            },
            ['ru', 'en'],
            id='ru, en',
        ),
    ),
)
async def test_client_info_web_ui_languages(
        taxi_cargo_corp,
        make_client_create_request,
        make_client_info_request,
        taxi_config,
        cargo_corp_country_specifics,
        web_ui_languages,
):
    taxi_config.set_values(
        {'CARGO_CORP_COUNTRY_SPECIFICS': cargo_corp_country_specifics},
    )
    await taxi_cargo_corp.invalidate_caches()

    response = await make_client_create_request(json=COMPANY_DATA)
    assert response.status_code == 200

    response = await make_client_info_request(is_internal=True)
    assert response.status_code == 200

    if web_ui_languages is None:
        assert 'web_ui_languages' not in response.json()
    else:
        assert response.json()['web_ui_languages'] == web_ui_languages


async def test_client_edit(
        taxi_cargo_corp, make_client_create_request, make_client_edit_request,
):
    request = {'company': {}}

    response = await make_client_create_request(json=request)
    assert response.status_code == 200

    request = COMPANY_DATA
    request['revision'] = response.json()['revision']

    response = await make_client_edit_request(
        client_id=utils.CORP_CLIENT_ID_2, json=request,
    )

    assert response.status_code == 404

    request['company']['emails'] = [{'text': 'hornsandhooves@yandex.ru'}]

    for _ in range(2):
        response = await make_client_edit_request(
            client_id=utils.CORP_CLIENT_ID_1, json=request,
        )
        assert response.status_code == 200
        request['corp_client_id'] = utils.CORP_CLIENT_ID_1
        request['revision'] = 2
        request_with_ts = {
            **request,
            **{
                'created_ts': matching.datetime_string,
                'updated_ts': matching.datetime_string,
            },
        }
        assert response.json() == request_with_ts
        request['revision'] = 1

    request['company']['name'] += '_edited'
    response = await make_client_edit_request(
        client_id=utils.CORP_CLIENT_ID_1, json=request,
    )
    assert response.status_code == 409


@pytest.mark.pgsql('cargo_corp', queries=[utils.get_client_create_request()])
async def test_client_remove(taxi_cargo_corp, make_client_remove_request):
    # idempotency
    for _ in range(2):
        response = await make_client_remove_request(utils.CORP_CLIENT_ID)
        assert response.status_code == 200

    # TODO (dipterix): check pg (employees)

    # not existing corp_client_id
    response = await make_client_remove_request(utils.CORP_CLIENT_ID[::-1])
    assert response.status_code == 200
