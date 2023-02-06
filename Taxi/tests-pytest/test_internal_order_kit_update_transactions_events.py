# coding: utf-8
from __future__ import unicode_literals
import datetime

import pytest

from taxi.core import async
from taxi.external import billing
from taxi.internal import card_operations
from taxi.internal.order_kit import const
from taxi.internal.order_kit import update_transactions_events
from cardstorage_mock import mock_cardstorage

import helpers


_NOW = datetime.datetime(2021, 5, 19, 17, 50, 0)
_MISSED_DEADLINE = _NOW - datetime.timedelta(seconds=1)
_NOT_YET_MISSED_DEADLINE = _NOW + datetime.timedelta(seconds=1)
_VERIFICATION_ID = 'verification-id'
_NO_CARDS_UID = '12345'
_BILLING_ERROR = object()
_EXPECTED_START_CHECK_CARD_CALLS = [
    {
        'args': (),
        'kwargs': {
            'billing_card_id': 'x988b7513b1b4235fb392377a',
            'currency': 'RUB',
            'log_extra': {'link': 'link1'},
            'region_id': 5,
            'service': 'card',
            'timeout': 2,
            'uber_uid': None,
            'user_ip': '::ffff:94.25.170.207',
            'yandex_uid': '4020890530',
        },
    },
]
_EXPECTED_FETCH_CHECK_CARD_STATUS_CALLS = [
    {
        'args': (),
        'kwargs': {
            'verification_id': _VERIFICATION_ID,
            'timeout': 2,
            'service': 'card',
            'log_extra': {'link': 'link1'},
        },
    },
]
_EXPECTED_UPDATE_TRANSACTIONS_EVENTS_CALLS = [
    {
        'args': (),
        'kwargs': {
            'eta': datetime.datetime(2021, 5, 19, 17, 50, 5),
            'events': [
                {
                    'antifraud_index': 0,
                    'event_name': 'poll_async_check_card',
                    'kwargs': {
                        'billing_id': 'x988b7513b1b4235fb392377a',
                        'currency': 'RUB',
                        'owner_uid': '4020890530',
                        'region_id': 5,
                        'uber_id': None,
                        'user_ip': '::ffff:94.25.170.207',
                        'verification_data': {
                            'deadline': (
                                datetime.datetime(2021, 5, 19, 17, 52)
                            ),
                            'verification_id': _VERIFICATION_ID,
                        },
                    },
                    'processing_index': 0
                }
            ],
            'log_extra': {'link': 'link1'},
            'order_id': 'order_id',
            'task_id': _VERIFICATION_ID,
        }
    }
]
_ASYNC_CHECK_CARD_SUCCESS_STATUS = (True, True)
_ASYNC_CHECK_CARD_ERROR_STATUS = (True, False)
_ASYNC_CHECK_CARD_IN_PROGRESS_STATUS = (False, False)


def _make_check_card_event(uid=None, verification_data=None):
    event_kwargs = {
        'owner_uid': uid if uid is not None else '4020890530',
        'billing_id': 'x988b7513b1b4235fb392377a',
        'user_ip': '::ffff:94.25.170.207',
        'region_id': 5,
        'currency': 'RUB',
        'uber_id': None,
    }
    event = {
        'event_name': const.EVENT_NAME_CHECK_CARD,
        'processing_index': 0,
        'antifraud_index': 0,
        'kwargs': event_kwargs,
    }
    if verification_data is not None:
        event['event_name'] = const.EVENT_NAME_POLL_ASYNC_CHECK_CARD
        event_kwargs['verification_data'] = verification_data
    return event


def _make_send_check_card_event_call(success):
    return {
        'args': (
            'stq',
            {
                'antifraud_index': 0,
                'order_id': 'order_id',
                'payment_id': 'card-x988b7513b1b4235fb392377a',
                'processing_index': 0,
                'region_id': 5,
                'success': success,
            },
        ),
        'kwargs': {
            'log_extra': {
                'link': 'link1'
            }
        }
    }


@pytest.mark.parametrize("success", [True, False])
@pytest.inline_callbacks
def test_check_card_event(success, patch):

    mock_cardstorage(patch)

    @patch('taxi.external.processing_antifraud.send_check_card_event')
    @async.inline_callbacks
    def send_check_card_event(src_tvm_service, json, *args, **kwargs):
        yield
        assert json == {
            'order_id': 'order_id',
            'processing_index': 0,
            'antifraud_index': 0,
            'payment_id': 'card-x988b7513b1b4235fb392377a',
            'region_id': 5,
            'success': success
        }

    @patch('taxi.external.billing._call_simple')
    def _call_simple(*args, **kwargs):
        return {
            'status': 'success' if success else 'fail',
            'trust_payment_id': 'tpi',
        }

    events = [_make_check_card_event()]
    yield update_transactions_events.update_transactions_events(
        'order_id', events, log_extra={'link': 'link1'}
    )


@pytest.inline_callbacks
def test_card_not_found(patch):

    mock_cardstorage(patch)

    @patch('taxi.external.processing_antifraud.send_check_card_event')
    @async.inline_callbacks
    def send_check_card_event(src_tvm_service, json, *args, **kwargs):
        yield

    @patch('taxi.external.billing._call_simple')
    def _call_simple(*args, **kwargs):
        return {'status': 'success'}

    events = [_make_check_card_event(uid=_NO_CARDS_UID)]
    with pytest.raises(update_transactions_events.CardNotFoundError):
        yield update_transactions_events.update_transactions_events(
            'order_id', events, log_extra={'link': 'link1'}
        )

    assert not send_check_card_event.calls
    assert not _call_simple.calls


class RaisesNoException(object):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


test_async_check_card_case = helpers.case_getter(
    'verification_data, start_check_card_response, '
    'fetch_check_card_status_response, expected_start_check_card_calls, '
    'expected_fetch_check_card_status_calls, '
    'expected_update_transactions_events_calls, '
    'expected_send_check_card_event_calls, expected_raises',
    # defaults
    verification_data=None,
    start_check_card_response=None,
    fetch_check_card_status_response=None,
    expected_start_check_card_calls=[],
    expected_fetch_check_card_status_calls=[],
    expected_update_transactions_events_calls=[],
    expected_send_check_card_event_calls=[],
    expected_raises=RaisesNoException(),
)


@pytest.mark.parametrize(
    test_async_check_card_case.params,
    [
        test_async_check_card_case(
            start_check_card_response=('in_progress', _VERIFICATION_ID),
            expected_start_check_card_calls=_EXPECTED_START_CHECK_CARD_CALLS,
            expected_update_transactions_events_calls=(
                _EXPECTED_UPDATE_TRANSACTIONS_EVENTS_CALLS
            ),
        ),
        test_async_check_card_case(
            verification_data={
                'verification_id': _VERIFICATION_ID,
                'deadline': _MISSED_DEADLINE,
            },
            fetch_check_card_status_response=(
                _ASYNC_CHECK_CARD_IN_PROGRESS_STATUS
            ),
            expected_fetch_check_card_status_calls=(
                _EXPECTED_FETCH_CHECK_CARD_STATUS_CALLS
            ),
            expected_send_check_card_event_calls=[
                _make_send_check_card_event_call(success=True),
            ],
        ),
        test_async_check_card_case(
            verification_data={
                'verification_id': _VERIFICATION_ID,
                'deadline': _MISSED_DEADLINE,
            },
            fetch_check_card_status_response=(
                _ASYNC_CHECK_CARD_ERROR_STATUS
            ),
            expected_fetch_check_card_status_calls=(
                _EXPECTED_FETCH_CHECK_CARD_STATUS_CALLS
            ),
            expected_send_check_card_event_calls=[
                _make_send_check_card_event_call(success=False),
            ],
        ),
        test_async_check_card_case(
            start_check_card_response=_BILLING_ERROR,
            expected_start_check_card_calls=_EXPECTED_START_CHECK_CARD_CALLS,
            expected_send_check_card_event_calls=[
                _make_send_check_card_event_call(success=True),
            ],
        ),
        test_async_check_card_case(
            start_check_card_response=('error', None),
            expected_start_check_card_calls=_EXPECTED_START_CHECK_CARD_CALLS,
            expected_send_check_card_event_calls=[
                _make_send_check_card_event_call(success=False),
            ],
        ),
        test_async_check_card_case(
            verification_data={
                'verification_id': _VERIFICATION_ID,
                'deadline': _NOT_YET_MISSED_DEADLINE,
            },
            fetch_check_card_status_response=_ASYNC_CHECK_CARD_SUCCESS_STATUS,
            expected_fetch_check_card_status_calls=(
                _EXPECTED_FETCH_CHECK_CARD_STATUS_CALLS
            ),
            expected_send_check_card_event_calls=[
                _make_send_check_card_event_call(success=True),
            ],
        ),
        test_async_check_card_case(
            verification_data={
                'verification_id': _VERIFICATION_ID,
                'deadline': _NOT_YET_MISSED_DEADLINE,
            },
            fetch_check_card_status_response=_ASYNC_CHECK_CARD_ERROR_STATUS,
            expected_fetch_check_card_status_calls=(
                _EXPECTED_FETCH_CHECK_CARD_STATUS_CALLS
            ),
            expected_send_check_card_event_calls=[
                _make_send_check_card_event_call(success=False),
            ],
        ),
        test_async_check_card_case(
            verification_data={
                'verification_id': _VERIFICATION_ID,
                'deadline': _NOT_YET_MISSED_DEADLINE,
            },
            fetch_check_card_status_response=_BILLING_ERROR,
            expected_fetch_check_card_status_calls=(
                _EXPECTED_FETCH_CHECK_CARD_STATUS_CALLS
            ),
            expected_raises=pytest.raises(card_operations.BillingError),
        ),
        test_async_check_card_case(
            verification_data={
                'verification_id': _VERIFICATION_ID,
                'deadline': _NOT_YET_MISSED_DEADLINE,
            },
            fetch_check_card_status_response=(
                _ASYNC_CHECK_CARD_IN_PROGRESS_STATUS
            ),
            expected_fetch_check_card_status_calls=(
                _EXPECTED_FETCH_CHECK_CARD_STATUS_CALLS
            ),
            expected_raises=pytest.raises(
                update_transactions_events.CheckCardStillInProgress,
            ),
        ),
    ]
)
@pytest.mark.config(
    BILLING_USE_ASYNC_CHECK_CARD={
        '__default__': False,
        'update_transactions_events': True,
    },
)
@pytest.mark.now(_NOW.isoformat())
@pytest.inline_callbacks
def test_async_check_card(patch, verification_data, start_check_card_response,
                          fetch_check_card_status_response,
                          expected_start_check_card_calls,
                          expected_fetch_check_card_status_calls,
                          expected_update_transactions_events_calls,
                          expected_send_check_card_event_calls,
                          expected_raises):

    mock_cardstorage(patch)

    @patch('taxi.external.processing_antifraud.send_check_card_event')
    @async.inline_callbacks
    def send_check_card_event(src_tvm_service, json, *args, **kwargs):
        yield

    @patch('taxi.external.billing.start_check_card')
    def start_check_card(*args, **kwargs):
        if start_check_card_response is _BILLING_ERROR:
            raise billing.BillingError('')
        return start_check_card_response

    @patch('taxi.external.billing.fetch_check_card_status')
    def fetch_check_card_status(*args, **kwargs):
        if fetch_check_card_status_response is _BILLING_ERROR:
            raise billing.BillingError('')
        return fetch_check_card_status_response

    @patch('taxi_stq.client.update_transactions_events')
    @async.inline_callbacks
    def stq_update_transactions_events(*args, **kwargs):
        yield

    events = [_make_check_card_event(verification_data=verification_data)]
    with expected_raises:
        yield update_transactions_events.update_transactions_events(
            'order_id', events, log_extra={'link': 'link1'}
        )

    assert start_check_card.calls == expected_start_check_card_calls
    assert fetch_check_card_status.calls == (
        expected_fetch_check_card_status_calls
    )
    assert stq_update_transactions_events.calls == (
        expected_update_transactions_events_calls
    )
    assert send_check_card_event.calls == expected_send_check_card_event_calls
