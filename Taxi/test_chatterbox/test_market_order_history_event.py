# pylint: disable=redefined-outer-name,too-many-arguments,too-many-lines
# pylint: disable=protected-access
import http
from typing import Dict
from typing import List
from typing import Optional

import bson
import pytest

from test_chatterbox import plugins as conftest


class Expect:
    def __init__(
            self,
            ticket: bool = False,
            tags: Optional[List[str]] = None,
            upload_pdf: bool = False,
            task_id: Optional[str] = None,
            task: Optional[Dict] = None,
            task_before: Optional[Dict] = None,
            tracker_transition_call: Optional[Dict] = None,
    ):
        self.tags = tags
        self.ticket = ticket
        self.upload_pdf = upload_pdf
        self.task_id = task_id
        self.task = task
        self.task_before = task_before
        self.tracker_transition_call = tracker_transition_call


@pytest.mark.config(
    CHATTERBOX_MARKET_EVENT_HANDLER_ENABLED={
        'pvz_receive_return': True,
        'b2b_preorder_confirmation': True,
        'b2b_remind_invoice_payment': True,
        'close_finished_returns': True,
        'open_ticket_on_created_return': True,
        'deferred_ticket_on_created_return': True,
    },
)
@pytest.mark.parametrize(
    'event_test_name, expected',
    [
        (
            'return_cancelled_return_close',
            Expect(
                task_id='5b2cae5cb2682a976914c211',
                task_before={'status': 'deferred'},
                task={'status': 'closed'},
                tracker_transition_call={
                    'ticket': 'MARKETYANDEX-2',
                    'kwargs': {'transition': 'close'},
                },
            ),
        ),
        (
            'b2b_remind_invoice_payment',
            Expect(ticket=True, tags=['market_b2b', 'b2b_remind_invoice']),
        ),
        (
            'b2b_remind_invoice_payment_close',
            Expect(
                task_id='5b2cae5cb2682a976914c210',
                task={'status': 'closed'},
                tracker_transition_call={
                    'ticket': 'MARKETYANDEX-1',
                    'kwargs': {'transition': 'close'},
                },
            ),
        ),
        (
            'b2b_preorder_confirmation',
            Expect(ticket=True, tags=['market_b2b', 'b2b_confirm_preorder']),
        ),
        (
            'return_delivery_post_track_needed',
            Expect(
                ticket=True,
                tags=['market_return', 'return_delivery_post_track_needed'],
                upload_pdf=True,
            ),
        ),
        (
            'fast_return_created',
            Expect(
                ticket=True,
                tags=['market_return', 'fast_return'],
                upload_pdf=True,
            ),
        ),
        (
            'pvz_received',
            Expect(
                ticket=True,
                tags=['market_return', 'pvz_receive'],
                upload_pdf=True,
            ),
        ),
        (
            'create_deferred',
            Expect(
                ticket=True,
                tags=['market_return', 'market_return_deferred'],
                upload_pdf=True,
            ),
        ),
    ],
)
async def test_event(
        event_test_name,
        expected: Expect,
        cbox: conftest.CboxWrap,
        db,
        mock_checkouter_return,
        load_json,
        mock_st_create_ticket,
        mock_st_create_comment,
        mock_st_upload_attachment,
        mock_st_transition,
        mock_checkouter_return_appl,
):
    async def _find_task():
        return await cbox.db.support_chatterbox.find_one(
            {'_id': bson.objectid.ObjectId(expected.task_id)},
        )

    if expected.task_before:
        task = await _find_task()
        for key, val in expected.task_before.items():
            assert task[key] == val

    _mock_st_upload_attachment = mock_st_upload_attachment('any')
    events = load_json('checkouter_order_history_events.json')[event_test_name]
    request = {'events': events}
    await cbox.post('/v1/market/order_history_event', data=request)
    assert cbox.status == http.HTTPStatus.NO_CONTENT

    if expected.ticket:
        call = mock_st_create_ticket.calls[0]
        assert set(call['kwargs'].get('tags', [])) == set(expected.tags or [])
    assert not mock_st_create_ticket.calls

    assert len(_mock_st_upload_attachment.calls) == (
        1 if expected.upload_pdf else 0
    )

    if expected.task_id:
        task = await _find_task()
        assert expected.task
        for key, value in expected.task.items():
            assert task[key] == value

    if expected.tracker_transition_call:
        call = mock_st_transition.calls[0]
        assert call['ticket'] == expected.tracker_transition_call['ticket']
        assert (
            call['kwargs']['transition']
            == expected.tracker_transition_call['kwargs']['transition']
        )
    assert not mock_st_transition.calls
