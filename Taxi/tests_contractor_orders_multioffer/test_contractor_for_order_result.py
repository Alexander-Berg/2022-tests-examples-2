import copy

import pytest


from tests_contractor_orders_multioffer import pg_helpers as pgh

PARAMS = {
    'allowed_classes': ['econom'],
    'order_id': 'order_id_0',
    'order': {'nearest_zone': 'moscow'},
    'lookup': {
        'generation': 1,
        'start_eta': 1604055148.006,
        'version': 2,
        'next_call_eta': 1604055164.614,
        'wave': 3,
    },
    'callback': {'url': 'some_url', 'timeout_ms': 500, 'attempts': 2},
}
MULTIOFFER_WINNER_ID = '66234567-89ab-cdef-0123-456789abcdef'


@pytest.mark.parametrize(
    'order_id', ['order_id_0', 'order_id_2', 'order_id_6'],
)
@pytest.mark.pgsql('contractor_orders_multioffer', files=pgh.ALL_FILES)
async def test_contractor_for_order_result_irrelevant(
        order_id, taxi_contractor_orders_multioffer,
):
    params = copy.deepcopy(PARAMS)
    params['order_id'] = 'order_id_0'
    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=params,
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'irrelevant'


@pytest.mark.pgsql('contractor_orders_multioffer', files=pgh.ALL_FILES)
async def test_contractor_for_order_result_delayed(
        taxi_contractor_orders_multioffer,
):
    params = copy.deepcopy(PARAMS)
    params['order_id'] = 'order_id_6'
    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=params,
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'delayed'


@pytest.mark.pgsql('contractor_orders_multioffer', files=pgh.ALL_FILES)
async def test_contractor_for_order_result_winner(
        taxi_config, taxi_contractor_orders_multioffer,
):
    params = copy.deepcopy(PARAMS)
    params['order_id'] = 'order_id_66'
    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=params,
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'found'
    assert response.json()['candidate'] == {
        'candidate_id': 'won_candidate',
        'metadata': {
            'multioffer': {
                'alias_id': 'alias_id1',
                'multioffer_id': MULTIOFFER_WINNER_ID,
            },
        },
    }


@pytest.mark.pgsql('contractor_orders_multioffer', files=pgh.ALL_FILES)
async def test_contractor_for_order_result_irrelevant_from_status(
        taxi_config, taxi_contractor_orders_multioffer,
):
    params = copy.deepcopy(PARAMS)
    params['order_id'] = 'order_id_7'
    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=params,
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'irrelevant'
