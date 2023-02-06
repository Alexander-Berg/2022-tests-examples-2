from typing import Any
from typing import Dict
from typing import Optional

import pytest


@pytest.fixture(name='request_retrieve_handle')
def request_retrieve_handle_fixture(taxi_passenger_feedback):
    async def _func(json_body: Dict[str, Any]):
        return await taxi_passenger_feedback.post(
            '/passenger-feedback/v1/retrieve', json_body,
        )

    return _func


EXPECTED_DB_ORDER_01 = {
    'rating': 3,
    'msg': 'message',
    'call_me': True,
    'app_comment': True,
    'is_after_complete': True,
    'choices': {
        'low_rating_reason': ['rudedriver'],
        'badge': ['pleasantmusic'],
    },
}

EXPECTED_DB_ORDER_02 = {'call_me': False, 'app_comment': True, 'choices': {}}

EXPECTED_YT_ORDER_01 = {
    'rating': 5,
    'msg': 'cool stuff',
    'call_me': False,
    'app_comment': True,
    'is_after_complete': True,
    'choices': {
        'low_rating_reason': ['rudedriver'],
        'badge': ['pleasantmusic'],
    },
}

EXPECTED_YT_ORDER_02 = {'call_me': False, 'app_comment': True, 'choices': {}}


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.yt(
    schemas=['yt_feedbacks_schema.yaml'], dyn_table_data=['yt_feedbacks.yaml'],
)
@pytest.mark.parametrize(
    ['order_id', 'from_archive', 'expected_status_code', 'expected_response'],
    [
        pytest.param(
            'unknown_order_id', True, 404, None, id='order_not_found',
        ),
        pytest.param(
            'db_order_01', False, 200, EXPECTED_DB_ORDER_01, id='by_order_id',
        ),
        pytest.param(
            'db_order_01_reorder',
            False,
            200,
            EXPECTED_DB_ORDER_01,
            id='by_reorder_id',
        ),
        pytest.param(
            'db_order_02',
            False,
            200,
            EXPECTED_DB_ORDER_02,
            id='missing_optional_fields',
        ),
        pytest.param('db_order_03', False, 404, None, id='no_data_in_order'),
        pytest.param('db_order_04', False, 404, None, id='invalid_data_type'),
        pytest.param(
            'yt_order_01',
            True,
            200,
            EXPECTED_YT_ORDER_01,
            id='yt_order_with_archive',
        ),
        pytest.param(
            'yt_order_01', False, 404, None, id='yt_order_without_archive',
        ),
        pytest.param(
            'yt_order_02',
            True,
            200,
            EXPECTED_YT_ORDER_02,
            id='yt_order_no_optional_fields',
        ),
        pytest.param(
            'yt_order_02_reorder',
            True,
            200,
            EXPECTED_YT_ORDER_02,
            id='yt_order_by_reorder_id',
        ),
    ],
)
async def test_retrieve(
        request_retrieve_handle,
        yt_apply,
        order_id: str,
        from_archive: bool,
        expected_status_code: int,
        expected_response: Optional[Dict[str, Any]],
):
    json_body = {'order_id': order_id, 'from_archive': from_archive}
    response = await request_retrieve_handle(json_body)
    assert response.status_code == expected_status_code
    if expected_response is not None:
        assert response.json() == expected_response


@pytest.mark.now('2018-08-10T21:01:30+0300')
@pytest.mark.config(FEEDBACK_ARCHIVATION_DELAY=60)
@pytest.mark.yt(
    schemas=['yt_feedbacks_schema.yaml'], dyn_table_data=['yt_feedbacks.yaml'],
)
@pytest.mark.parametrize(
    ['order_due', 'expected_status_code'],
    [
        pytest.param(None, 200, id='no_order_due'),
        pytest.param('2018-08-10T21:00:00+0300', 200, id='old_order_due'),
        pytest.param('2018-08-10T21:01:00+0300', 404, id='recent_order_due'),
    ],
)
async def test_order_due(
        request_retrieve_handle,
        yt_apply,
        order_due: Optional[str],
        expected_status_code: int,
):
    json_body = {'order_id': 'yt_order_01', 'from_archive': True}
    if order_due is not None:
        json_body['order_due'] = order_due
    response = await request_retrieve_handle(json_body)
    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        assert response.json() == EXPECTED_YT_ORDER_01
