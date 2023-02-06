import pytest

from tests_cargo_corp import utils

BILLING_ID = 'BILLING_ID'


async def prepare_billing_client(make_client_balance_upsert_request):
    request = {'billing_id': BILLING_ID, 'contract': utils.PHOENIX_CONTRACT}
    response = await make_client_balance_upsert_request(
        utils.CORP_CLIENT_ID, request,
    )
    assert response.status_code == 200


def set_mocked_cargo_tasks(mocked_cargo_tasks, load_json):
    mocked_cargo_tasks.get_public_tariff.set_expected_data(
        {
            'client_id': utils.CORP_CLIENT_ID,
            'zone_name': 'moscow',
            'country': 'rus',
            'locale': 'ru',
        },
    )
    mocked_cargo_tasks.get_public_tariff.set_response(
        200, load_json('get_public_tariff.json'),
    )
    mocked_cargo_tasks.get_client_tariff.set_expected_data(
        {
            'client_id': utils.CORP_CLIENT_ID,
            'zone_name': 'moscow',
            'country': 'rus',
            'locale': 'ru',
        },
    )
    mocked_cargo_tasks.get_client_tariff.set_response(
        200, load_json('get_client_tariff.json'),
    )


@pytest.mark.parametrize(
    ('is_billing_client', 'response_json'),
    (
        pytest.param(False, 'get_public_tariff.json', id='card client'),
        pytest.param(True, 'get_client_tariff.json', id='billing client'),
    ),
)
async def test_tariffs(
        taxi_cargo_corp,
        mocked_cargo_tasks,
        make_client_balance_upsert_request,
        load_json,
        is_billing_client,
        response_json,
):
    if is_billing_client:
        await prepare_billing_client(make_client_balance_upsert_request)

    set_mocked_cargo_tasks(mocked_cargo_tasks, load_json)

    response = await taxi_cargo_corp.post(
        '/v1/client/tariff',
        headers={
            'Accept-Language': 'ru',
            'X-B2B-Client-Id': utils.CORP_CLIENT_ID,
        },
        json={'zone_name': 'moscow', 'country': 'rus'},
    )
    assert response.status_code == 200

    if is_billing_client:
        assert mocked_cargo_tasks.get_public_tariff_times_called == 0
        assert mocked_cargo_tasks.get_client_tariff_times_called == 1
    else:
        assert mocked_cargo_tasks.get_public_tariff_times_called == 1
        assert mocked_cargo_tasks.get_client_tariff_times_called == 0

    assert response.json() == load_json(response_json)
