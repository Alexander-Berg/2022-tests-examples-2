import pytest

from tests_cargo_pricing.next_day_delivery import utils

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.config(
        CARGO_PRICING_DB_SOURCES_FOR_READ={
            'v1/next-day-delivery/calc/retrieve': ['pg'],
        },
    ),
    pytest.mark.config(
        CURRENCY_ROUNDING_RULES={
            'ILS': {'__default__': 0.1},
            '__default__': {'__default__': 0.01},
        },
    ),
]


@pytest.fixture(name='retrieve_ndd_calcs')
def _retrieve_ndd_calcs(
        taxi_cargo_pricing,
        default_calcplan_config,
        mock_ndd_tariff_composer_retrieve,
):
    async def ndd_calc(calc_ids: list):
        response = await taxi_cargo_pricing.post(
            '/v1/next-day-delivery/calc/retrieve', json={'calc_ids': calc_ids},
        )
        assert response.status_code == 200
        return response.json()

    return ndd_calc


@pytest.fixture(name='create_ndd_calc')
def _create_ndd_calc(v1_ndd_calc_client_creator, default_calcplan_config):
    async def ndd_calc(idempotency_token: str = 'token'):
        v1_ndd_calc_client_creator.payload[
            'idempotency_token'
        ] = idempotency_token
        create_resp = await v1_ndd_calc_client_creator.execute()
        assert create_resp.status_code == 200
        return create_resp.json()

    return ndd_calc


def assert_retrieve_result(retrieve_result, idempotency_token='token'):
    assert retrieve_result['price'] == utils.get_default_calculated_price()
    assert retrieve_result['tariff'] == utils.get_default_tariff_composition()
    assert retrieve_result['details']['services'] == []
    assert retrieve_result['diagnostics'][
        'calc_request'
    ] == utils.get_default_calc_request(idempotency_token)
    assert (
        retrieve_result['stages']['calc_plan']
        == utils.get_default_calcplan_config()['plan']
    )


async def test_bulk_retrieve_calc(create_ndd_calc, retrieve_ndd_calcs):
    calc = await create_ndd_calc()
    resp = await retrieve_ndd_calcs(calc_ids=[calc['calculation']['id']])
    assert resp['calculations'][0]['calc_id'] == calc['calculation']['id']
    assert_retrieve_result(resp['calculations'][0]['result'])


async def test_bulk_retrieve_calcs(create_ndd_calc, retrieve_ndd_calcs):
    calcs = []
    idempotency_tokens = ['token1', 'token2']
    idempotency_tokens_map = {}

    for num in range(2):
        token = idempotency_tokens[num]
        calc = await create_ndd_calc(token)
        calcs.append(calc)
        idempotency_tokens_map[calc['calculation']['id']] = token

    resp = await retrieve_ndd_calcs(
        [calc['calculation']['id'] for calc in calcs],
    )

    calcs = sorted(calcs, key=lambda calc: calc['calculation']['id'])
    resp_calcs = sorted(resp['calculations'], key=lambda calc: calc['calc_id'])

    for i in range(2):
        assert resp_calcs[i]['calc_id'] == calcs[i]['calculation']['id']
        assert_retrieve_result(
            resp_calcs[i]['result'],
            idempotency_tokens_map[resp_calcs[i]['calc_id']],
        )


async def test_bulk_retrieve_calc_not_valid_id(
        create_ndd_calc, retrieve_ndd_calcs,
):
    calc = await create_ndd_calc()
    not_valid_id = (
        'cargo-pricing/ndd/v1/' + '00000000-0000-0000-0000-000000000000'
    )
    resp = await retrieve_ndd_calcs([calc['calculation']['id'], not_valid_id])

    error_resp_calc = resp['calculations'][0]
    success_resp_calc = resp['calculations'][1]
    if success_resp_calc['calc_id'] == not_valid_id:
        error_resp_calc, success_resp_calc = success_resp_calc, error_resp_calc

    assert error_resp_calc['calc_id'] == not_valid_id
    assert error_resp_calc['result']['code'] == 'not_found'
    assert success_resp_calc['calc_id'] == calc['calculation']['id']
    assert_retrieve_result(success_resp_calc['result'])
