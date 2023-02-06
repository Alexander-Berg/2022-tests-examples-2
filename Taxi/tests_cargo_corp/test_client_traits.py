import pytest  # noqa: F401

LOCAL_CARD_ID = 'LOCAL_CARD_ID'
BILLING_ID = 'BILLING_ID'
PERSON_ID = 'PERSON_ID'
LOCAL_CARD_ID_NOT_REGISTERED = 'LOCAL_CARD_ID_NOT_REGISTERED'

LOCAL_CLIENT_ID_CARD = 'long_corp_client_id_length_32_01'
LOCAL_CLIENT_ID_BILLING = 'long_corp_client_id_length_32_02'
LOCAL_CLIENT_ID_NOT_REGISTERED = 'long_corp_client_id_length_32_03'

LOCAL_CLIENT_WITH_CARD = {
    'id': LOCAL_CLIENT_ID_CARD,
    'name': 'test_corp_client_name',
    'is_registration_finished': True,
}

LOCAL_CLIENT_WITH_BILLING = {
    'id': LOCAL_CLIENT_ID_BILLING,
    'name': 'test_corp_client_name',
    'is_registration_finished': True,
}

LOCAL_CLIENT_NOT_REGISTERED = {
    'id': LOCAL_CLIENT_ID_NOT_REGISTERED,
    'name': 'test_corp_client_name_not_registrated',
    'is_registration_finished': False,
}


async def prepare_clients(
        prepare_multiple_clients, make_client_balance_upsert_request,
):
    prepare_multiple_clients([LOCAL_CLIENT_WITH_CARD], card_id=LOCAL_CARD_ID)
    prepare_multiple_clients([LOCAL_CLIENT_WITH_BILLING])
    prepare_multiple_clients(
        [LOCAL_CLIENT_NOT_REGISTERED], card_id=LOCAL_CARD_ID_NOT_REGISTERED,
    )

    response = await make_client_balance_upsert_request(
        LOCAL_CLIENT_ID_BILLING, {'billing_id': BILLING_ID},
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'corp_client_id, is_small_business',
    [
        (LOCAL_CLIENT_ID_CARD, True),
        (LOCAL_CLIENT_ID_BILLING, False),
        (LOCAL_CLIENT_ID_NOT_REGISTERED, False),
    ],
)
async def test_client_traits(
        taxi_cargo_corp,
        prepare_multiple_clients,
        make_client_balance_upsert_request,
        make_client_traits_request,
        corp_client_id,
        is_small_business,
):
    await prepare_clients(
        prepare_multiple_clients, make_client_balance_upsert_request,
    )

    response = await make_client_traits_request(corp_client_id)
    assert response.status_code == 200

    result = response.json()
    assert result['is_small_business'] == is_small_business
