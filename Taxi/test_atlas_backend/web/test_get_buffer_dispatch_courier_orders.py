import json
from typing import Any
from typing import Dict
from typing import List

import pytest


@pytest.mark.config(
    ATLAS_BACKEND_BUFFER_DISPATCH_COURIERS={
        'cluster': 'hahn',
        'cluster_alias': '*ch_public',
        'attempts': 2,
        'timeout_ms': 60 * 1000,
        'delay_ms': 1000,
        'queries_limit': {
            'get_couriers_orders': 10000,
            'get_couriers_positions': 100000,
            'get_courier_orders': 10000,
        },
    },
)
async def test_get_buffer_dispatch_courier_orders(
        web_app_client, atlas_blackbox_mock, patch, open_file,
) -> None:
    @patch('client_chyt.components.AsyncChytClient.execute')
    # pylint: disable=W0612
    async def execute(*args, **kwargs) -> List[Dict[str, Any]]:
        with open_file('get_courier_orders_response.json') as file_:
            return json.load(file_)

    response = await web_app_client.post(
        '/api/v2/buffer-dispatch/courier-orders',
        json={'courier_id': '20078983', 'date': '2022-04-05'},
    )
    assert response.status == 200
    actual_result = await response.json()
    with open_file('expected_result.json') as expected_result_file:
        expected_result = json.load(expected_result_file)
        for courier in actual_result['orders']:
            assert courier in expected_result
