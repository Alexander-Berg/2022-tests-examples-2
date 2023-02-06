import datetime
import typing

import pytest

NOW = datetime.datetime(2022, 5, 18, 17, 5, 1, 104308)


def debts_processing_call(
        order_id: str,
        event: str,
        event_time: datetime.datetime,
        reason_code=None,
        log_extra: typing.Optional[dict] = None,
):
    assert order_id == 'invoice_id_1'
    assert event == 'set_debt'
    assert event_time == {'$date': '2022-05-18T17:05:01.104Z'}


@pytest.mark.parametrize(
    'order_id,was_stq_request',
    [
        ('invoice_id_2', False),
        ('invoice_id_1', True),
        ('not_debt_order', False),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_basic(
        debts_client,
        order_id,
        was_stq_request,
        stq,
        mock_transactions_invoice_retrieve,
):
    code = await debts_client.admin_make_debt(order_id=order_id)
    assert code == 200

    assert stq.debts_processing.times_called == int(was_stq_request)

    if was_stq_request:
        request_pararms = stq.debts_processing.next_call()
        assert request_pararms['queue'] == 'debts_processing'
        assert request_pararms['id'] == order_id
        debts_processing_call(*request_pararms['args'])


async def test_non_exist_order_id(
        debts_client, mock_transactions_invoice_retrieve,
):
    code = await debts_client.admin_make_debt(order_id='non_exist_order_id')
    assert code == 404
