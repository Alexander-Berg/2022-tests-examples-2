import uuid

import pytest

TASK_ID = '5GMix9mn36g1hlQtb40FoJ3DYsCZuYrk4'
PLACE_ID = 'oBk3xjmoTB3pw2fwf7gc17xWv3BIXupGHx7tJ4ztF7g'


@pytest.mark.parametrize(
    'request_data, code',
    [
        (
            {
                'place_group_id': uuid.uuid4().hex,
                'place_id': uuid.uuid4().hex,
                'task_type': 'availability',
                'forwarded_data': {'origin_place_id': uuid.uuid4().hex},
            },
            200,
        ),
        (
            {
                'place_group_id': uuid.uuid4().hex,
                'place_id': uuid.uuid4().hex,
                'task_type': 'availability',
                'forwarded_data': {},
            },
            400,
        ),
        ({}, 400),
    ],
)
async def test_post_task(web_app_client, web_context, request_data, code):
    response = await web_app_client.post(
        '/v1/start-parsing?task_uuid=taskuuid', json=request_data,
    )
    assert response.status == code
