import pytest

from tests_cargo_corp import utils

LOCAL_CARD_ID = 'LOCAL_CARD_ID'
BILLING_ID = 'BILLING_ID'
PERSON_ID = 'PERSON_ID'

LOCAL_CLIENT_ID = 'long_corp_client_id_length_32_01'
LOCAL_CLIENT_ID_BILLING = 'long_corp_client_id_length_32_02'

LOCAL_YANDEX_UID = 'LOCAL_YANDEX_UID_1'
LOCAL_YANDEX_UID_BILLING = 'LOCAL_YANDEX_UID_BILLING'

LOCAL_CLIENT = {'id': LOCAL_CLIENT_ID, 'name': 'test_corp_client_name'}
LOCAL_CLIENT_DATA = {
    'id': LOCAL_CLIENT_ID,
    'name': 'test_corp_client_name',
    'is_registration_finished': True,
    'employee': {'phone_pd_id': utils.PHONE_PD_ID},
}

LOCAL_CLIENT_BILLING = {
    'id': LOCAL_CLIENT_ID_BILLING,
    'name': 'test_corp_client_name',
}
LOCAL_CLIENT_DATA_BILLING = {
    'id': LOCAL_CLIENT_ID_BILLING,
    'name': 'test_corp_client_name',
    'is_registration_finished': True,
    'employee': {'phone_pd_id': utils.PHONE_PD_ID},
}

CARGO_CORP_COUNTRY_SPECIFICS = {
    'rus': {'balance_info': {'balance_domain': 'ru'}},
}


async def prepare_clients(
        prepare_multiple_clients, make_client_balance_upsert_request,
):
    prepare_multiple_clients(
        [LOCAL_CLIENT_DATA],
        yandex_uid=LOCAL_YANDEX_UID,
        card_id=LOCAL_CARD_ID,
    )
    prepare_multiple_clients(
        [LOCAL_CLIENT_DATA_BILLING], yandex_uid=LOCAL_YANDEX_UID_BILLING,
    )

    request = {'billing_id': BILLING_ID, 'contract': utils.PHOENIX_CONTRACT}
    response = await make_client_balance_upsert_request(
        LOCAL_CLIENT_ID_BILLING, request,
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    (
        'corp_client_id',
        'yandex_uid',
        'expected_code',
        'expected_response',
        'country_specifics',
        'balance_domain',
    ),
    (
        pytest.param(
            LOCAL_CLIENT_ID,
            LOCAL_YANDEX_UID,
            404,
            {'code': '', 'message': ''},
            CARGO_CORP_COUNTRY_SPECIFICS,
            'ru',
            id='card client',
        ),
        pytest.param(
            LOCAL_CLIENT_ID_BILLING,
            LOCAL_YANDEX_UID_BILLING,
            200,
            {'user_path': 'https://yandex.ru'},
            CARGO_CORP_COUNTRY_SPECIFICS,
            'ru',
            id='billing client ru',
        ),
        pytest.param(
            LOCAL_CLIENT_ID_BILLING,
            LOCAL_YANDEX_UID_BILLING,
            200,
            {'user_path': 'https://yandex.com'},
            {},
            'com',
            id='billing client com',
        ),
    ),
)
async def test_create_prepay_invoice(
        taxi_cargo_corp,
        taxi_config,
        user_has_rights,
        register_default_user,
        register_default_card,
        mocked_cargo_tasks,
        make_client_balance_upsert_request,
        prepare_multiple_clients,
        corp_client_id,
        yandex_uid,
        expected_code,
        expected_response,
        country_specifics,
        balance_domain,
):
    taxi_config.set_values({'CARGO_CORP_COUNTRY_SPECIFICS': country_specifics})
    await taxi_cargo_corp.invalidate_caches()

    await prepare_clients(
        prepare_multiple_clients, make_client_balance_upsert_request,
    )

    mocked_cargo_tasks.create_prepay_invoice.set_response(
        200, {'user_path': 'https://yandex.' + balance_domain},
    )
    mocked_cargo_tasks.create_prepay_invoice.set_expected_data(
        {
            'amount': 1.0,
            'client_id': 'BILLING_ID',
            'contract_id': '12345',
            'operator_uid': yandex_uid,
            'region': balance_domain,
        },
    )

    response = await taxi_cargo_corp.post(
        '/v1/client/create-prepay-invoice',
        headers={
            'X-B2B-Client-Id': corp_client_id,
            'X-Yandex-UID': yandex_uid,
        },
        json={'amount': 1},
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert mocked_cargo_tasks.create_prepay_invoice_times_called == 1
    else:
        assert mocked_cargo_tasks.create_prepay_invoice_times_called == 0

    response_json = response.json()
    assert response_json == expected_response
