import uuid

import pytest

from eats_place_groups_replica.internal import exceptions
from eats_place_groups_replica.stq import create_task

TASK_ID = 'task'
TASK_ID2 = 'task2'
PLACE_ID = 'place_id'
PLACE_ID2 = 'place_id2'


def rand_id():
    return uuid.uuid4().hex


@pytest.mark.parametrize(
    'request_data, has_calls',
    [
        ({'id': rand_id(), 'type': 'price', 'place_id': PLACE_ID}, True),
        ({'id': rand_id(), 'type': 'stock', 'place_id': PLACE_ID}, True),
        (
            {'id': rand_id(), 'type': 'availability', 'place_id': PLACE_ID},
            True,
        ),
        (
            {'id': rand_id(), 'type': 'nomenclature', 'place_id': PLACE_ID},
            True,
        ),
        ({'id': rand_id(), 'type': 'discount', 'place_id': PLACE_ID}, True),
        ({'id': rand_id(), 'type': 'price', 'place_id': rand_id()}, False),
        ({'id': TASK_ID, 'type': 'price', 'place_id': PLACE_ID}, True),
        ({'id': TASK_ID2, 'type': 'price', 'place_id': PLACE_ID2}, False),
        ({'id': TASK_ID, 'type': 'price', 'place_id': rand_id()}, False),
    ],
)
@pytest.mark.config(
    EATS_PLACE_GROUPS_REPLICA_PARSER_NAMES={'parser_name': 'retail'},
)
async def test_create_task(
        mock_processing, stq3_context, stq_task_info, request_data, has_calls,
):
    @mock_processing('/v1/eda/integration_menu_processing/create-event')
    def create_event(request):
        if request.query.get('json'):
            assert request.query['json'] == 'retail'
        return {'event_id': request.query['item_id']}

    await create_task.task(stq3_context, stq_task_info, task=request_data)
    assert create_event.has_calls == has_calls


@pytest.mark.config(
    EATS_PLACE_GROUPS_REPLICA_PARSER_NAMES={'parser_name': 'retail'},
)
async def test_post_identical_task(stq3_context, stq_task_info):
    with pytest.raises(exceptions.IdenticalTaskNotFinished):
        await create_task.task(
            stq3_context,
            stq_task_info,
            task={'id': TASK_ID, 'type': 'nomenclature', 'place_id': PLACE_ID},
        )
