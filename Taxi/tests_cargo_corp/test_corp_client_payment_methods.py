import pytest

from tests_cargo_corp import utils

LOCAL_CARD_ID_1 = 'LOCAL_CARD_ID_1'
LOCAL_CARD_ID_2 = 'LOCAL_CARD_ID_2'
BILLING_ID = 'BILLING_ID'
PERSON_ID = 'PERSON_ID'
LOCAL_CARD_ID_NOT_REGISTERED = 'LOCAL_CARD_ID_NOT_REGISTERED'

LOCAL_CLIENT_ID_1 = 'long_corp_client_id_length_32_01'
LOCAL_CLIENT_ID_2 = 'long_corp_client_id_length_32_02'
LOCAL_CLIENT_ID_BILLING = 'long_corp_client_id_length_32_03'
LOCAL_CLIENT_ID_NOT_REGISTERED = 'long_corp_client_id_length_32_04'

LOCAL_YANDEX_UID_1 = 'LOCAL_YANDEX_UID_1'
LOCAL_YANDEX_UID_2 = 'LOCAL_YANDEX_UID_2'
LOCAL_YANDEX_UID_BILLING = 'LOCAL_YANDEX_UID_BILLING'
LOCAL_YANDEX_UID_NOT_REGISTERED = 'LOCAL_YANDEX_UID_NOT_REGISTERED'

LOCAL_CLIENT_1 = {'id': LOCAL_CLIENT_ID_1, 'name': 'test_corp_client_name'}
LOCAL_CLIENT_DATA_1 = {
    'id': LOCAL_CLIENT_ID_1,
    'name': 'test_corp_client_name',
    'is_registration_finished': True,
    'employee': {'phone_pd_id': utils.PHONE_PD_ID},
}

LOCAL_CLIENT_2 = {'id': LOCAL_CLIENT_ID_2, 'name': 'test_corp_client_name'}
LOCAL_CLIENT_DATA_2 = {
    'id': LOCAL_CLIENT_ID_2,
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

LOCAL_CLIENT_NOT_REGISTERED = {
    'id': LOCAL_CLIENT_ID_NOT_REGISTERED,
    'name': 'test_corp_client_name_not_registrated',
}
LOCAL_CLIENT_NOT_REGISTERED_DATA = {
    'id': LOCAL_CLIENT_ID_NOT_REGISTERED,
    'name': 'test_corp_client_name_not_registrated',
    'is_registration_finished': False,
    'employee': {'phone_pd_id': utils.PHONE_PD_ID},
}

DIFFERENT_YANDEX_UIDS = 'Способ оплаты недоступен по техническим причинам'


def get_headers(
        corp_client_id=None,
        yandex_uid=None,
        phone_pd_id=None,
        request_mode=None,
):
    headers = {'Accept-Language': 'ru'}
    if corp_client_id:
        headers['X-B2B-Client-Id'] = corp_client_id
    if yandex_uid:
        headers['X-Yandex-Uid'] = yandex_uid
    if phone_pd_id:
        headers['Phone-Pd-Id'] = phone_pd_id
    if request_mode:
        headers['X-Request-Mode'] = request_mode
    return headers


async def prepare_clients(
        prepare_multiple_clients, make_client_balance_upsert_request,
):
    prepare_multiple_clients(
        [LOCAL_CLIENT_DATA_1],
        yandex_uid=LOCAL_YANDEX_UID_1,
        card_id=LOCAL_CARD_ID_1,
    )
    prepare_multiple_clients(
        [LOCAL_CLIENT_DATA_2],
        yandex_uid=LOCAL_YANDEX_UID_2,
        card_id=LOCAL_CARD_ID_2,
    )
    prepare_multiple_clients(
        [LOCAL_CLIENT_DATA_BILLING], yandex_uid=LOCAL_YANDEX_UID_BILLING,
    )
    prepare_multiple_clients(
        [LOCAL_CLIENT_NOT_REGISTERED_DATA],
        yandex_uid=LOCAL_YANDEX_UID_NOT_REGISTERED,
        card_id=LOCAL_CARD_ID_NOT_REGISTERED,
    )

    request = {'billing_id': BILLING_ID, 'contract': utils.PHOENIX_CONTRACT}
    response = await make_client_balance_upsert_request(
        LOCAL_CLIENT_ID_BILLING, request,
    )
    assert response.status_code == 200


@pytest.mark.config(
    CARGO_CORP_ROLL_OUT_OPTIONS_ENABLED={'is_worker_by_phones_ready': True},
)
@pytest.mark.parametrize(
    'yandex_uid, phone_pd_id, payment_methods',
    (
        pytest.param('other_uid', None, [], id='search by other_uid'),
        pytest.param(
            LOCAL_YANDEX_UID_1,
            None,
            [
                {
                    'corp_info': {
                        'corp_client_id': LOCAL_CLIENT_1['id'],
                        'corp_client_name': LOCAL_CLIENT_1['name'],
                        'country': 'rus',
                    },
                    'card_info': {
                        'card_id': LOCAL_CARD_ID_1,
                        'yandex_uid': LOCAL_YANDEX_UID_1,
                    },
                },
            ],
            id='search by LOCAL_YANDEX_UID_1',
        ),
        pytest.param(
            LOCAL_YANDEX_UID_BILLING,
            None,
            [
                {
                    'corp_info': {
                        'corp_client_id': LOCAL_CLIENT_BILLING['id'],
                        'corp_client_name': LOCAL_CLIENT_BILLING['name'],
                        'country': 'rus',
                    },
                    'contract_info': {
                        'billing_id': BILLING_ID,
                        'contract_id': utils.PHOENIX_CONTRACT['id'],
                        'contract_type': utils.PHOENIX_CONTRACT['kind'],
                        'payment_type': utils.PHOENIX_CONTRACT['payment_type'],
                    },
                },
            ],
            id='search by LOCAL_YANDEX_UID_BILLING',
        ),
        pytest.param(
            LOCAL_YANDEX_UID_1,
            utils.PHONE_PD_ID,
            [
                {
                    'corp_info': {
                        'corp_client_id': LOCAL_CLIENT_BILLING['id'],
                        'corp_client_name': LOCAL_CLIENT_BILLING['name'],
                        'country': 'rus',
                    },
                    'reason_for_unavailability': {
                        'code': 'different_yandex_uids',
                        'message': DIFFERENT_YANDEX_UIDS,
                    },
                },
                {
                    'corp_info': {
                        'corp_client_id': LOCAL_CLIENT_2['id'],
                        'corp_client_name': LOCAL_CLIENT_2['name'],
                        'country': 'rus',
                    },
                    'reason_for_unavailability': {
                        'code': 'different_yandex_uids',
                        'message': DIFFERENT_YANDEX_UIDS,
                    },
                },
                {
                    'corp_info': {
                        'corp_client_id': LOCAL_CLIENT_1['id'],
                        'corp_client_name': LOCAL_CLIENT_1['name'],
                        'country': 'rus',
                    },
                    'card_info': {
                        'card_id': LOCAL_CARD_ID_1,
                        'yandex_uid': LOCAL_YANDEX_UID_1,
                    },
                },
            ],
            id='search by LOCAL_YANDEX_UID_1 and PHONE_PD_ID',
        ),
        pytest.param(
            'other_uid',
            utils.PHONE_PD_ID,
            [
                {
                    'corp_info': {
                        'corp_client_id': LOCAL_CLIENT_BILLING['id'],
                        'corp_client_name': LOCAL_CLIENT_BILLING['name'],
                        'country': 'rus',
                    },
                    'reason_for_unavailability': {
                        'code': 'different_yandex_uids',
                        'message': DIFFERENT_YANDEX_UIDS,
                    },
                },
                {
                    'corp_info': {
                        'corp_client_id': LOCAL_CLIENT_2['id'],
                        'corp_client_name': LOCAL_CLIENT_2['name'],
                        'country': 'rus',
                    },
                    'reason_for_unavailability': {
                        'code': 'different_yandex_uids',
                        'message': DIFFERENT_YANDEX_UIDS,
                    },
                },
                {
                    'corp_info': {
                        'corp_client_id': LOCAL_CLIENT_1['id'],
                        'corp_client_name': LOCAL_CLIENT_1['name'],
                        'country': 'rus',
                    },
                    'reason_for_unavailability': {
                        'code': 'different_yandex_uids',
                        'message': DIFFERENT_YANDEX_UIDS,
                    },
                },
            ],
            id='search by other_uid and PHONE_PD_ID',
        ),
    ),
)
async def test_corp_client_payment_methods(
        taxi_cargo_corp,
        user_has_rights,
        register_default_user,
        register_default_card,
        make_client_balance_upsert_request,
        prepare_multiple_clients,
        yandex_uid,
        phone_pd_id,
        payment_methods,
):
    await prepare_clients(
        prepare_multiple_clients, make_client_balance_upsert_request,
    )

    response = await taxi_cargo_corp.post(
        '/internal/cargo-corp/v1/employee/corp-client/payment-methods/list',
        headers=get_headers(yandex_uid=yandex_uid, phone_pd_id=phone_pd_id),
    )
    assert response.status_code == 200

    response_json = response.json()['payment_methods']
    for item in response_json:
        item['corp_info'].pop('created_ts')

    assert response_json == payment_methods
