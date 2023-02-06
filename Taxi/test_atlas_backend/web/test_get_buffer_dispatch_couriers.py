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
async def test_get_buffer_dispatch_couriers(
        web_app_client, atlas_blackbox_mock, patch, open_file,
) -> None:
    @patch('client_chyt.components.AsyncChytClient.execute')
    # pylint: disable=W0612
    async def execute(query: str, *args, **kwargs) -> List[Dict[str, Any]]:
        file_name = None
        if '//home/eda-analytics/reasome/datalens/dm_order_90_d' in query:
            file_name = (
                'get_order_response.json'
                if 'WHERE "order_id" =' in query
                else 'get_couriers_orders_response.json'
            )
        elif (
            '//home/eda-dwh/export/courier_analytics/courier_coordinate'
            in query
        ):
            file_name = 'get_couriers_positions_response.json'
        elif (
            '//home/eda-analytics/reasome/'
            'united_dispatch/cte/shift_cte_enriched' in query
        ):
            file_name = 'get_shifts_response.json'

        if not file_name:
            return []

        with open_file(file_name) as file_:
            return json.load(file_)

    response = await web_app_client.post(
        '/api/v2/buffer-dispatch/couriers', json={'order_id': '7869124853'},
    )
    assert response.status == 200
    actual_result = await response.json()
    with open_file('expected_result.json') as expected_result_file:
        expected_result = json.load(expected_result_file)
        for courier in actual_result['couriers']:
            assert courier in expected_result
