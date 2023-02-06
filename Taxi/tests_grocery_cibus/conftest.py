# pylint: disable=wildcard-import, unused-wildcard-import, import-error

import typing

from grocery_mocks.utils import helpers as mock_helpers
import pytest

from grocery_cibus_plugins import *  # noqa: F403 F401

from . import consts


@pytest.fixture
def run_deferred_cancel(mockserver, stq_runner):
    async def _inner(
            expect_fail: bool = False,
            exec_tries: typing.Optional[int] = None,
            invoice_id=consts.ORDER_ID,
            token=consts.DEFAULT_TOKEN,
            **kwargs,
    ):
        kwargs = {'invoice_id': invoice_id, 'token': token, **kwargs}

        await stq_runner.grocery_cibus_deferred_cancel.call(
            task_id='task_id',
            kwargs=kwargs,
            expect_fail=expect_fail,
            exec_tries=exec_tries,
        )

    return _inner


@pytest.fixture
def check_deferred_cancel_stq_event(stq):
    def _inner(times_called=1, stq_event_id=None, **kwargs):
        assert stq.grocery_cibus_deferred_cancel.times_called == times_called
        if times_called == 0:
            return

        args = stq.grocery_cibus_deferred_cancel.next_call()
        if stq_event_id is not None:
            assert args['id'] == stq_event_id

        if args['kwargs'] is not None:
            _check_kwargs(args['kwargs'], kwargs)

    return _inner


def _check_kwargs(args, kwargs):
    mock_helpers.assert_dict_contains(args, kwargs)
