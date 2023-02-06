import datetime
from typing import Any

import pytest

from generated.clients import transactions_eda

from iiko_integration.generated.stq3 import stq_context
from iiko_integration.logic import transactions as transactions_logic
from iiko_integration.stq import update_transactions
from test_iiko_integration import transactions_stubs as stubs


NOW = datetime.datetime(2042, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)

# pylint: disable=invalid-name
pytestmark = [pytest.mark.now(NOW.isoformat())]


def invoice_retrieve_response_data(response_extra_data=None):
    if response_extra_data is None:
        response_extra_data = {}
    return {**stubs.DEFAULT_INVOICE_RETRIEVE_RESPONSE, **response_extra_data}


def invoice_update_request_data(invoice_id):
    return {**stubs.DEFAULT_INVOICE_UPDATE_REQUEST, 'id': invoice_id}


ORDER_FIELDS = ['changelog']


class DbChecker:

    # pylint: disable=attribute-defined-outside-init
    async def init_db_order(self, invoice_id, get_db_order):
        self.get_db_order = get_db_order
        self.invoice_id = invoice_id
        self.initial_order = await get_db_order(
            fields=ORDER_FIELDS, invoice_id=invoice_id,
        )

    async def _check_order(self, expected_order):
        order = await self.get_db_order(
            fields=ORDER_FIELDS, invoice_id=self.invoice_id,
        )
        if order:
            for index, change_event in enumerate(expected_order['changelog']):
                change_event['updated_at'] = order['changelog'][index][
                    'updated_at'
                ]
        assert order == expected_order

    async def check_after(self):
        pass


class DbOrderIsNotChanged(DbChecker):
    async def check_after(self):
        await self._check_order(self.initial_order)


class DbOrderIsChanged(DbChecker):
    async def check_after(self):
        expected_order = self.initial_order
        event = expected_order['changelog'][1]
        event['status'] = 'processing'
        event['operation_id'] = 'refund_2'
        event['updated_at'] = NOW
        await self._check_order(expected_order)


class NotError:
    pass


@pytest.fixture(name='test_task')
def test_task_fixture(mockserver, stq3_context, get_db_order):
    async def _test_task_fixture(
            invoice_id,
            expected_error_class=NotError,
            db_checker: DbChecker = None,
    ):
        @mockserver.json_handler('/user_api-api/users/get')
        def _user_get(request):
            return {'has_ya_plus': True}

        if db_checker:
            await db_checker.init_db_order(
                invoice_id=invoice_id, get_db_order=get_db_order,
            )
        error: Any = NotError()
        try:
            await update_transactions.task(
                context=stq3_context, invoice_id=invoice_id,
            )
        # pylint: disable=broad-except
        except Exception as exc:
            error = exc
            if not isinstance(error, expected_error_class):
                raise
        assert isinstance(error, expected_error_class)

        if db_checker:
            await db_checker.check_after()

    return _test_task_fixture


@pytest.mark.parametrize(
    ['invoice_id', 'invoice_retrieve_response', 'invoice_update_request'],
    [
        (
            'order_pending',
            stubs.DEFAULT_INVOICE_RETRIEVE_RESPONSE,
            stubs.DEFAULT_INVOICE_UPDATE_REQUEST,
        ),
        (
            'order_pending_composite',
            stubs.COMPOSITE_INVOICE_RETRIEVE_RESPONSE,
            stubs.COMPOSITE_INVOICE_UPDATE_REQUEST,
        ),
    ],
)
async def test_task_successfully_finished(
        stq3_context: stq_context.Context,
        mock_invoice_retrieve,
        mock_invoice_update,
        test_task,
        invoice_id: str,
        invoice_retrieve_response: dict,
        invoice_update_request: dict,
):

    invoice_retrieve = mock_invoice_retrieve(
        invoice_id=invoice_id, response_data=invoice_retrieve_response,
    )
    invoice_update = mock_invoice_update(
        expected_request_data=invoice_update_request,
    )

    await test_task(invoice_id=invoice_id, db_checker=DbOrderIsChanged())

    assert invoice_retrieve.times_called == 1
    assert invoice_update.times_called == 1


@pytest.mark.parametrize(
    [
        'invoice_id',
        'invoice_extra_data',
        'invoice_retrieve_response_code',
        'invoice_update_response_code',
        'invoice_update_called',
    ],
    [
        pytest.param(
            'order_pending',
            {},
            404,
            200,
            False,
            id='invoice_not_found_while_getting_invoice',
        ),
        pytest.param(
            'order_pending',
            {},
            200,
            404,
            True,
            id='invoice_not_found_while_updating_invoice',
        ),
        pytest.param(
            'order_pending',
            {'yandex_uid': '111222333'},
            200,
            200,
            False,
            id='user_mismatch',
        ),
        pytest.param(
            'order_pending',
            {
                'sum_to_pay': [
                    *stubs.default_sum_to_pay(),
                    {**stubs.default_sum_to_pay()[0], 'payment_type': 'cash'},
                ],
            },
            200,
            200,
            False,
            id='invoice_validation_error_2_payment_types',
        ),
        pytest.param(
            'invoice_not_in_db', {}, 200, 200, False, id='invoice_not_in_db',
        ),
        pytest.param(
            'order_processing', {}, 200, 200, False, id='order_is_processed',
        ),
        pytest.param(
            'order_done', {}, 200, 200, False, id='no_pending_changes',
        ),
    ],
)
async def test_task_unsuccessfully_finished(
        invoice_id: str,
        invoice_extra_data: dict,
        invoice_retrieve_response_code: int,
        invoice_update_response_code: int,
        invoice_update_called: bool,
        stq3_context,
        mock_invoice_retrieve,
        mock_invoice_update,
        test_task,
        mockserver,
):

    invoice_retrieve = mock_invoice_retrieve(
        invoice_id=invoice_id,
        response_data=invoice_retrieve_response_data(invoice_extra_data),
        response_code=invoice_retrieve_response_code,
    )
    invoice_update = mock_invoice_update(
        expected_request_data=invoice_update_request_data(
            invoice_id=invoice_id,
        ),
        response_code=invoice_update_response_code,
    )

    await test_task(invoice_id=invoice_id, db_checker=DbOrderIsNotChanged())

    assert invoice_retrieve.times_called == 1

    if invoice_update_called:
        assert invoice_update.times_called == 1
    else:
        assert invoice_update.times_called == 0


@pytest.mark.parametrize(
    ['invoice_update_response_code', 'error'],
    [
        pytest.param(
            409,
            transactions_logic.ConflictError,
            id='invoice_update_conflict',
        ),
        pytest.param(
            500,
            transactions_eda.NotDefinedResponse,
            id='invoice_failed_to_update',
        ),
    ],
)
async def test_task_failed(
        invoice_update_response_code,
        error,
        stq3_context,
        mock_invoice_retrieve,
        mock_invoice_update,
        test_task,
        monkeypatch,
):
    invoice_id = 'order_pending'
    invoice_retrieve = mock_invoice_retrieve(
        invoice_id=invoice_id, response_data=invoice_retrieve_response_data(),
    )
    invoice_update = mock_invoice_update(
        expected_request_data=invoice_update_request_data(
            invoice_id=invoice_id,
        ),
        response_code=invoice_update_response_code,
    )

    await test_task(
        invoice_id=invoice_id,
        expected_error_class=error,
        db_checker=DbOrderIsNotChanged(),
    )

    assert invoice_retrieve.times_called == 1
    assert invoice_update.times_called == 1
