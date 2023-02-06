# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import typing

import pytest

from eats_simple_payments_plugins import *  # noqa: F403 F401


@pytest.fixture(name='mock_transactions_invoice_bad_retrieve')
def _mock_transactions_invoice_bad_retrieve(mockserver, request):
    code = request.param

    @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
    def _transactions_invoice_retrieve(request):
        return mockserver.make_response(
            **{
                'status': code,
                'json': {'message': 'error message', 'code': str(code)},
            },
        )


@pytest.fixture()
def insert_items(pgsql):
    def _insert_items(items: typing.List[dict]):
        item_fields = [
            'item_id',
            'order_id',
            'place_id',
            'balance_client_id',
            'type',
        ]

        def _build_value(item: dict) -> str:
            item_values = [item[field] for field in item_fields]
            sql_values = [f'\'{value}\'' for value in item_values]
            return ','.join(sql_values)

        inserted_item_fields = ', '.join(item_fields)
        inserted_values = ','.join(f'({_build_value(item)})' for item in items)
        query = (
            f'INSERT INTO eats_simple_payments.items_info'
            f' ({inserted_item_fields})'
            f' VALUES {inserted_values}'
        )
        cursor = pgsql['eats_simple_payments'].cursor()
        cursor.execute(query)

    return _insert_items


# pylint: disable=invalid-name
@pytest.fixture(name='check_send_receipt')
def check_send_receipt_fixture(stq_runner, stq):
    async def _inner(
            send_receipt_times_called,
            task_id: typing.Optional[str] = None,
            exec_tries: typing.Optional[int] = None,
    ):
        assert (
            stq.eats_simple_payments_send_receipt.times_called
            == send_receipt_times_called
        )
        for _ in range(send_receipt_times_called):
            next_call = stq.eats_simple_payments_send_receipt.next_call()
            next_task_id = next_call['id']
            if task_id is not None:
                assert task_id == next_task_id
            kwargs = next_call['kwargs']
            await stq_runner.eats_simple_payments_send_receipt.call(
                task_id=next_task_id, kwargs=kwargs, exec_tries=exec_tries,
            )

    return _inner
