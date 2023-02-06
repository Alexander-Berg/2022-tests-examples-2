import pytest  # noqa: F401

from tests_cargo_corp import utils


@pytest.mark.parametrize(
    ('corp_client_id', 'expected_code', 'expected_json'),
    [
        pytest.param(utils.CORP_CLIENT_ID, 200, {}, id='OK'),
        pytest.param(
            utils.CORP_CLIENT_ID_1,
            404,
            {'code': 'not_found', 'message': 'Unknown corp_client'},
            id='client_not_found',
        ),
    ],
)
async def test_upsert_balance_info(
        make_client_balance_upsert_request,
        get_client_balance_info,
        corp_client_id,
        expected_code,
        expected_json,
):
    request = {'billing_id': utils.BILLING_ID, 'person_id': utils.PERSON_ID}

    response = await make_client_balance_upsert_request(
        corp_client_id, request,
    )
    assert response.status_code == expected_code
    assert response.json() == expected_json
    if expected_code != 200:
        return

    # update contract info
    request = {
        'billing_id': utils.BILLING_ID,
        'contract': utils.PHOENIX_CONTRACT,
    }
    response = await make_client_balance_upsert_request(
        corp_client_id, request,
    )
    assert response.status_code == expected_code
    assert response.json() == expected_json

    balance_info_from_db = get_client_balance_info(corp_client_id)
    assert balance_info_from_db == (
        utils.BILLING_ID,
        utils.PERSON_ID,
        utils.PHOENIX_CONTRACT['id'],
        utils.PHOENIX_CONTRACT['external_id'],
        utils.PHOENIX_CONTRACT['kind'],
        utils.PHOENIX_CONTRACT['payment_type'],
    )


async def test_upsert_balance_info_stub(
        make_client_balance_upsert_request, get_client_balance_info,
):
    """
    Test for temp balance info stub.
    """

    request = {
        'billing_id': utils.BILLING_ID,
        'person_id': '',
        'contract': {
            'id': '',
            'external_id': '',
            'kind': 'offer',
            'payment_type': 'prepaid',
        },
    }

    response = await make_client_balance_upsert_request(
        utils.CORP_CLIENT_ID, request,
    )
    assert response.status_code == 200
    assert response.json() == {}

    balance_info_from_db = get_client_balance_info(utils.CORP_CLIENT_ID)
    assert balance_info_from_db == (
        utils.BILLING_ID,
        '',
        None,
        None,
        'offer',
        'prepaid',
    )
