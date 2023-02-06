import http

import pytest

from chatterbox.internal.tasks_manager import _constants
from test_chatterbox import plugins as conftest


@pytest.mark.parametrize(
    'order_return_id, comment', [('2384728', 'confirmed')],
)
async def test_add_return_comment(
        cbox: conftest.CboxWrap, db, order_return_id, comment,
):
    async def find_task():
        return await db.support_chatterbox.find_one(
            {'meta_info.order_return_id': order_return_id},
        )

    task = await find_task()
    assert 'inner_comments' not in task
    assert task['status'] == _constants.STATUS_DEFERRED

    await cbox.post(
        '/v1/market/return_comment',
        params={'order_return_id': order_return_id, 'request_id': '1'},
        data={'text': comment},
    )
    assert cbox.status == http.HTTPStatus.NO_CONTENT

    task = await find_task()
    assert task['inner_comments'][-1]['comment'] == comment
    assert task['status'] == _constants.STATUS_REOPENED


@pytest.mark.parametrize('tag', [None, 'from_external_comment'])
async def test_new_ticket_on_comment(
        cbox: conftest.CboxWrap,
        db,
        mock_st_create_ticket,
        mock_st_create_comment,
        mock_checkouter_return,
        mock_checkouter_order,
        mock_checkouter_return_appl,
        mock_st_upload_attachment,
        tag,
):
    _mock_st_upload_attachment = mock_st_upload_attachment('any')
    order_return_id = '123'
    comment = 'confirmed'
    query_params = {'order_return_id': order_return_id, 'request_id': '1'}
    if tag:
        query_params['tag'] = tag
    await cbox.post(
        '/v1/market/return_comment',
        params=query_params,
        data={'text': comment},
    )
    assert cbox.status == http.HTTPStatus.NO_CONTENT

    assert _mock_st_upload_attachment.calls[0]

    call = mock_st_create_ticket.calls[0]
    expect_tags = {'market_return'}
    if tag:
        expect_tags.add(tag)
    assert set(call['kwargs']['tags']) == expect_tags
    assert call['kwargs']['custom_fields']['OrderReturnId'] == '123'

    call = mock_st_create_comment.calls[0]
    assert call['kwargs']['text'] == comment


async def test_add_return_comment_empty_body_request(cbox, db):
    await cbox.post(
        '/v1/market/return_comment',
        params={'order_return_id': '2384728', 'request_id': '1'},
    )
    assert cbox.status == http.HTTPStatus.BAD_REQUEST


async def test_add_return_comment_missing_field_request(cbox, db):
    await cbox.post(
        '/v1/market/return_comment',
        params={'order_return_id': '2384728', 'request_id': '1'},
        data={},
    )
    assert cbox.status == http.HTTPStatus.BAD_REQUEST
