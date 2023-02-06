import uuid

import pytest

from eats_integration_menu_schema import parser_tools


@pytest.mark.parametrize(
    'request_data, code',
    [
        (
            {
                'place_group_id': uuid.uuid4().hex,
                'place_id': uuid.uuid4().hex,
                'brand_id': uuid.uuid4().hex,
                'task_type': 'availability',
                'forwarded_data': {},
            },
            400,
        ),
        ({}, 400),
        (
            {
                'place_group_id': uuid.uuid4().hex,
                'place_id': uuid.uuid4().hex,
                'brand_id': uuid.uuid4().hex,
                'task_type': 'availability',
                'forwarded_data': {'origin_place_id': uuid.uuid4().hex},
            },
            200,
        ),
        (
            {
                'place_group_id': uuid.uuid4().hex,
                'place_id': uuid.uuid4().hex,
                'brand_id': uuid.uuid4().hex,
                'task_type': 'stock',
                'forwarded_data': {'origin_place_id': uuid.uuid4().hex},
            },
            200,
        ),
        (
            {
                'place_group_id': uuid.uuid4().hex,
                'place_id': uuid.uuid4().hex,
                'brand_id': uuid.uuid4().hex,
                'task_type': 'price',
                'forwarded_data': {'origin_place_id': uuid.uuid4().hex},
            },
            200,
        ),
        (
            {
                'place_group_id': uuid.uuid4().hex,
                'place_id': uuid.uuid4().hex,
                'brand_id': uuid.uuid4().hex,
                'task_type': 'nomenclature',
                'forwarded_data': {'origin_place_id': uuid.uuid4().hex},
            },
            200,
        ),
    ],
)
async def test_post_task(web_app_client, web_context, request_data, code, stq):
    queues = {
        parser_tools.TaskType.AVAILABILITY.value: (
            stq.eats_retail_globus_parser_availability
        ),
        parser_tools.TaskType.STOCK.value: (
            stq.eats_retail_globus_parser_stocks
        ),
        parser_tools.TaskType.NOMENCLATURE.value: (
            stq.eats_retail_globus_parser_nomenclature
        ),
        parser_tools.TaskType.PRICE.value: (
            stq.eats_retail_globus_parser_prices
        ),
    }

    response = await web_app_client.post(
        '/v1/start-parsing?task_uuid=task_uuid', json=request_data,
    )

    assert response.status == code
    if code == 200:
        assert queues[request_data['task_type']].has_calls
