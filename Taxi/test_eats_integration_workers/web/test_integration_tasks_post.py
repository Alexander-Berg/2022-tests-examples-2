import uuid

import pytest

TASK_ID = '5GMix9mn36g1hlQtb40FoJ3DYsCZuYrk4'
PLACE_ID = 'oBk3xjmoTB3pw2fwf7gc17xWv3BIXupGHx7tJ4ztF7g'


@pytest.mark.parametrize(
    'request_data, code',
    [
        (
            {
                'id': uuid.uuid4().hex,
                'type': 'price',
                'place_id': uuid.uuid4().hex,
            },
            400,
        ),
        ({'id': uuid.uuid4().hex, 'type': 'price', 'place_id': PLACE_ID}, 200),
        ({'id': TASK_ID, 'type': 'price', 'place_id': PLACE_ID}, 200),
        ({'id': TASK_ID, 'type': 'price', 'place_id': uuid.uuid4().hex}, 400),
        ({'id': TASK_ID, 'type': 'nomenclature', 'place_id': PLACE_ID}, 409),
    ],
)
async def test_post_task(web_app_client, web_context, request_data, code):
    response = await web_app_client.post('/v1/tasks', json=request_data)
    assert response.status == code


@pytest.mark.parametrize(
    'request_data, stq_queue',
    [
        (
            {'id': uuid.uuid4().hex, 'type': 'price', 'place_id': PLACE_ID},
            'eats_integration_workers_price',
        ),
        (
            {
                'id': uuid.uuid4().hex,
                'type': 'nomenclature',
                'place_id': PLACE_ID,
            },
            'eats_integration_workers_nomenclature',
        ),
        (
            {
                'id': uuid.uuid4().hex,
                'type': 'availability',
                'place_id': PLACE_ID,
            },
            'eats_integration_workers_availability',
        ),
        (
            {'id': uuid.uuid4().hex, 'type': 'stock', 'place_id': PLACE_ID},
            'eats_integration_workers_stocks',
        ),
    ],
)
async def test_should_call_correct_stq(
        web_app_client, stq_runner, request_data, stq_queue, stq,
):
    mocks = [
        'eats_integration_workers_price',
        'eats_integration_workers_availability',
        'eats_integration_workers_stocks',
        'eats_integration_workers_nomenclature',
    ]

    await web_app_client.post('/v1/tasks', json=request_data)

    for queue_name in mocks:
        if queue_name == stq_queue:
            assert getattr(stq, queue_name).has_calls
        else:
            assert not getattr(stq, queue_name).has_calls
