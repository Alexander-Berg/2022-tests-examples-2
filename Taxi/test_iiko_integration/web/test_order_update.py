# pylint: disable=too-many-lines
import copy
import dataclasses
import decimal
from typing import List
from typing import Optional

import pytest

from iiko_integration import const
from iiko_integration.model import order as order_model
from test_iiko_integration import stubs


@dataclasses.dataclass
class AllowedTransitionCases:
    order_id: str
    invoice_transitions: List['InvoiceTransitionCase']
    restaurant_transitions: List['RestaurantTransitionCase']


@dataclasses.dataclass
class InvoiceTransitionCase:
    new_status: str
    response_code: int = 200
    changed_restaurant_status: Optional[str] = None
    stq_calls: Optional[List[str]] = None
    empty_change_events_after: bool = False


@dataclasses.dataclass
class RestaurantTransitionCase:
    new_status: str
    response_code: int = 200
    stq_calls: Optional[List[str]] = None
    empty_change_events_after: bool = False


ALL_INVOICE_STATUSES = {status.value for status in order_model.InvoiceStatus}


ALL_RESTAURANT_STATUSES = {
    status.value for status in order_model.RestaurantStatus
}

ALL_IIKO_STATUSES = {
    status.value for status in order_model.IIKO_TO_REST_STATUS_MAP
}

# do not check start_payment here
ALLOWED_STATUS_TRANSITION_CASES = {
    ('INIT', 'PENDING'): AllowedTransitionCases(
        '01',
        [],
        [
            RestaurantTransitionCase('CLOSED', empty_change_events_after=True),
            RestaurantTransitionCase(
                'CANCELED', empty_change_events_after=True,
            ),
        ],
    ),
    ('INIT', 'CANCELED'): AllowedTransitionCases(
        '03',
        [],
        [RestaurantTransitionCase('CANCELED', empty_change_events_after=True)],
    ),
    ('INIT', 'CLOSED'): AllowedTransitionCases(
        '04',
        [],
        [RestaurantTransitionCase('CLOSED', empty_change_events_after=True)],
    ),
    ('HOLDING', 'PENDING'): AllowedTransitionCases(
        '05',
        [
            InvoiceTransitionCase('HOLDING'),
            InvoiceTransitionCase(
                'HELD',
                changed_restaurant_status='WAITING_FOR_CONFIRMATION',
                stq_calls=['restaurant_order_expired'],
            ),
            InvoiceTransitionCase(
                'HOLD_FAILED', empty_change_events_after=True,
            ),
        ],
        [
            RestaurantTransitionCase('CLOSED', empty_change_events_after=True),
            RestaurantTransitionCase(
                'CANCELED', empty_change_events_after=True,
            ),
        ],
    ),
    ('HOLDING', 'CLOSED'): AllowedTransitionCases(
        '05.1',
        [
            InvoiceTransitionCase('HOLDING'),
            InvoiceTransitionCase('HELD', stq_calls=['cancel_order_called']),
            InvoiceTransitionCase(
                'HOLD_FAILED', empty_change_events_after=True,
            ),
        ],
        [RestaurantTransitionCase('CLOSED', empty_change_events_after=True)],
    ),
    ('HOLDING', 'CANCELED'): AllowedTransitionCases(
        '05.2',
        [
            InvoiceTransitionCase('HOLDING'),
            InvoiceTransitionCase('HELD', stq_calls=['cancel_order_called']),
            InvoiceTransitionCase(
                'HOLD_FAILED', empty_change_events_after=True,
            ),
        ],
        [RestaurantTransitionCase('CANCELED', empty_change_events_after=True)],
    ),
    ('HELD', 'WAITING_FOR_CONFIRMATION'): AllowedTransitionCases(
        '06',
        [
            InvoiceTransitionCase(
                'HELD', stq_calls=['restaurant_order_expired'],
            ),
            # unexpected states, but possible:
            InvoiceTransitionCase(
                'CLEARING', stq_calls=['restaurant_order_expired'],
            ),
            InvoiceTransitionCase(
                'CLEARED',
                stq_calls=[
                    'process_cleared_called',
                    'restaurant_order_expired',
                ],
            ),
        ],
        [
            RestaurantTransitionCase(
                'CLOSED',
                stq_calls=['cancel_order_called'],
                empty_change_events_after=True,
            ),
            RestaurantTransitionCase(
                'CANCELED',
                stq_calls=['cancel_order_called'],
                empty_change_events_after=True,
            ),
            RestaurantTransitionCase(
                'PAYMENT_CONFIRMED', stq_calls=['close_order_called'],
            ),
        ],
    ),
    ('HELD', 'PAYMENT_CONFIRMED'): AllowedTransitionCases(
        '07',
        [
            InvoiceTransitionCase('HELD', stq_calls=['close_order_called']),
            InvoiceTransitionCase('CLEARING'),
            InvoiceTransitionCase(
                'CLEARED', stq_calls=['process_cleared_called'],
            ),
        ],
        [
            RestaurantTransitionCase(
                'PAYMENT_CONFIRMED', stq_calls=['close_order_called'],
            ),
        ],
    ),
    ('HELD', 'CLOSED'): AllowedTransitionCases(
        '07.1',
        [
            InvoiceTransitionCase('HELD', stq_calls=['cancel_order_called']),
            InvoiceTransitionCase('CLEARING'),
            InvoiceTransitionCase(
                'CLEARED', stq_calls=['process_cleared_called'],
            ),
        ],
        [
            RestaurantTransitionCase(
                'CLOSED',
                stq_calls=['cancel_order_called'],
                empty_change_events_after=True,
            ),
        ],
    ),
    ('HELD', 'CANCELED'): AllowedTransitionCases(
        '07.2',
        [
            InvoiceTransitionCase('HELD', stq_calls=['cancel_order_called']),
            InvoiceTransitionCase('CLEARING'),
            InvoiceTransitionCase(
                'CLEARED', stq_calls=['process_cleared_called'],
            ),
        ],
        [
            RestaurantTransitionCase(
                'CANCELED',
                stq_calls=['cancel_order_called'],
                empty_change_events_after=True,
            ),
        ],
    ),
    ('HOLD_FAILED', 'PENDING'): AllowedTransitionCases(
        '08',
        [InvoiceTransitionCase('HOLD_FAILED', empty_change_events_after=True)],
        [
            RestaurantTransitionCase(
                'CANCELED', empty_change_events_after=True,
            ),
            RestaurantTransitionCase('CLOSED', empty_change_events_after=True),
        ],
    ),
    ('HOLD_FAILED', 'CLOSED'): AllowedTransitionCases(
        '08.1',
        [InvoiceTransitionCase('HOLD_FAILED', empty_change_events_after=True)],
        [RestaurantTransitionCase('CLOSED', empty_change_events_after=True)],
    ),
    ('HOLD_FAILED', 'CANCELED'): AllowedTransitionCases(
        '08.2',
        [InvoiceTransitionCase('HOLD_FAILED', empty_change_events_after=True)],
        [RestaurantTransitionCase('CANCELED', empty_change_events_after=True)],
    ),
    ('CLEARING', 'PAYMENT_CONFIRMED'): AllowedTransitionCases(
        '09',
        [
            InvoiceTransitionCase('CLEARING'),
            InvoiceTransitionCase(
                'CLEARED', stq_calls=['process_cleared_called'],
            ),
        ],
        [RestaurantTransitionCase('PAYMENT_CONFIRMED')],
    ),
    ('CLEARING', 'CLOSED'): AllowedTransitionCases(
        '09.1',
        [
            InvoiceTransitionCase('CLEARING'),
            InvoiceTransitionCase(
                'CLEARED', stq_calls=['process_cleared_called'],
            ),
        ],
        [RestaurantTransitionCase('CLOSED', empty_change_events_after=True)],
    ),
    ('CLEARING', 'CANCELED'): AllowedTransitionCases(
        '09.2',
        [
            InvoiceTransitionCase('CLEARING'),
            InvoiceTransitionCase(
                'CLEARED', stq_calls=['process_cleared_called'],
            ),
        ],
        [RestaurantTransitionCase('CANCELED', empty_change_events_after=True)],
    ),
    ('CLEARED', 'PAYMENT_CONFIRMED'): AllowedTransitionCases(
        '10',
        [
            InvoiceTransitionCase(
                'CLEARED', stq_calls=['process_cleared_called'],
            ),
            InvoiceTransitionCase('REFUNDING'),
        ],
        [RestaurantTransitionCase('PAYMENT_CONFIRMED')],
    ),
    ('CLEARED', 'CLOSED'): AllowedTransitionCases(
        '10.1',
        [
            InvoiceTransitionCase(
                'CLEARED', stq_calls=['process_cleared_called'],
            ),
            # unexpected now, but maybe in future:
            InvoiceTransitionCase('REFUNDING'),
        ],
        [RestaurantTransitionCase('CLOSED', empty_change_events_after=True)],
    ),
    ('CLEARED', 'CANCELED'): AllowedTransitionCases(
        '10.2',
        [
            InvoiceTransitionCase(
                'CLEARED', stq_calls=['process_cleared_called'],
            ),
            # unexpected now, but maybe in future:
            InvoiceTransitionCase('REFUNDING'),
        ],
        [RestaurantTransitionCase('CANCELED', empty_change_events_after=True)],
    ),
    ('REFUNDING', 'PAYMENT_CONFIRMED'): AllowedTransitionCases(
        '42',
        [
            InvoiceTransitionCase(
                'CLEARED', stq_calls=['process_cleared_called'],
            ),
            InvoiceTransitionCase('REFUNDING'),
        ],
        [RestaurantTransitionCase('PAYMENT_CONFIRMED')],
    ),
}


# is_restaurant=False: pytest.param(order_id, operation_id, invoice_case)
# is_restaurant=True: pytest.param(order_id, restaurnt_case)
def all_cases_params(is_restaurant=False):
    result = []
    for invoice_status in ALL_INVOICE_STATUSES:
        for restaurant_status in ALL_RESTAURANT_STATUSES:
            order_cases = ALLOWED_STATUS_TRANSITION_CASES.get(
                (invoice_status, restaurant_status),
            )
            if not order_cases:
                continue
            if is_restaurant:
                failure_case_statuses = copy.deepcopy(ALL_IIKO_STATUSES)
                ok_cases = order_cases.restaurant_transitions
            else:
                failure_case_statuses = copy.deepcopy(ALL_INVOICE_STATUSES)
                failure_case_statuses.remove('INIT')
                ok_cases = order_cases.invoice_transitions

            for ok_case in ok_cases:
                failure_case_statuses.remove(ok_case.new_status)
                new_status = ok_case.new_status
                if is_restaurant:
                    result.append(
                        pytest.param(
                            order_cases.order_id,
                            ok_case,
                            id=(
                                f'{invoice_status}+{restaurant_status}'
                                f'->{new_status}:OK'
                            ),
                        ),
                    )
                else:
                    result.append(
                        pytest.param(
                            order_cases.order_id,
                            None,
                            ok_case,
                            id=(
                                f'{invoice_status}+{restaurant_status}'
                                f'->{new_status}:OK'
                            ),
                        ),
                    )
                    result.append(
                        pytest.param(
                            order_cases.order_id,
                            '1',
                            ok_case,
                            id=(
                                f'{invoice_status}+{restaurant_status}'
                                f'->{new_status}&correct_operation_id:OK'
                            ),
                        ),
                    )
                    if invoice_status != 'HOLD_FAILED':
                        result.append(
                            pytest.param(
                                order_cases.order_id,
                                'wrong_id',
                                InvoiceTransitionCase(
                                    new_status=ok_case.new_status,
                                    response_code=409,
                                ),
                                id=(
                                    f'{invoice_status}+{restaurant_status}'
                                    f'->{new_status}&incorrect_operation_id:'
                                    'FAILURE'
                                ),
                            ),
                        )
                    else:
                        result.append(
                            pytest.param(
                                order_cases.order_id,
                                'wrong_id',
                                ok_case,
                                id=(
                                    f'{invoice_status}+{restaurant_status}'
                                    f'->{new_status}&incorrect_operation_id:'
                                    'OK'
                                ),
                            ),
                        )

            for failure_case_status in failure_case_statuses:
                if is_restaurant:
                    result.append(
                        pytest.param(
                            order_cases.order_id,
                            RestaurantTransitionCase(
                                new_status=failure_case_status,
                                response_code=409,
                            ),
                            id=(
                                f'{invoice_status}+{restaurant_status}'
                                f'->{failure_case_status}:FAILURE'
                            ),
                        ),
                    )
                else:
                    result.append(
                        pytest.param(
                            order_cases.order_id,
                            None,
                            InvoiceTransitionCase(
                                new_status=failure_case_status,
                                response_code=409,
                            ),
                            id=(
                                f'{invoice_status}+{restaurant_status}'
                                f'->{failure_case_status}:FAILURE'
                            ),
                        ),
                    )

    if is_restaurant:
        result.append(
            pytest.param(
                'not_exist',
                RestaurantTransitionCase(
                    new_status='CLOSED', response_code=404,
                ),
                id='Not found',
            ),
        )
    else:
        result.append(
            pytest.param(
                'not_exist',
                None,
                InvoiceTransitionCase(new_status='HOLDING', response_code=404),
                id='Not found',
            ),
        )

    return result


ORDER_FIELDS = [
    'status',
    'status_history',
    'invoice_id',
    'yandex_uid',
    'user_id',
    'payment_method_type',
    'payment_method_id',
    'complement_payment_method_type',
    'complement_payment_method_id',
    'complement_amount',
    'changelog',
    'locale',
    'personal_email_id',
    'total_price',
    'items',
    'version',
]


class DbChecker:

    # pylint: disable=attribute-defined-outside-init
    async def init_db_order(self, order_id, get_db_order):
        self.get_db_order = get_db_order
        self.order_id = order_id
        self.initial_order = await get_db_order(
            fields=ORDER_FIELDS, id=order_id,
        )

    async def _check_order(
            self,
            expected_order,
            check_changelog_body=True,
            empty_change_events_after=False,
    ):
        order = await self.get_db_order(fields=ORDER_FIELDS, id=self.order_id)
        invoice_updated_at = order['status']['invoice_updated_at']
        restaurant_updated_at = order['status']['restaurant_updated_at']
        expected_order['status']['invoice_updated_at'] = invoice_updated_at
        expected_order['status'][
            'restaurant_updated_at'
        ] = restaurant_updated_at
        expected_order['status_history'][-1][
            'restaurant_updated_at'
        ] = restaurant_updated_at
        expected_order['status_history'][-1][
            'invoice_updated_at'
        ] = invoice_updated_at

        if empty_change_events_after and self.initial_order['changelog']:
            expected_order['changelog'] = []
            expected_order['version'] += 1

        assert len(expected_order['changelog']) == len(order['changelog'])
        if not check_changelog_body:
            expected_order['changelog'] = order['changelog']
        elif order['changelog']:
            expected_order['changelog'][-1]['updated_at'] = order['changelog'][
                -1
            ]['updated_at']
            expected_order['changelog'][-1]['created_at'] = order['changelog'][
                -1
            ]['created_at']

        assert order == expected_order

    async def check_after(self):
        pass


class DbOrderIsNotChanged(DbChecker):
    async def check_after(self):
        expected_order = copy.deepcopy(self.initial_order)
        await self._check_order(expected_order)


class DbOrderVersionChanged(DbChecker):
    async def check_after(self):
        expected_order = copy.deepcopy(self.initial_order)
        expected_order['version'] = self.initial_order['version'] + 1
        await self._check_order(expected_order)


class DbOrderIsChangedByRestaurant(DbChecker):
    def __init__(
            self,
            expected_restaurant_status: str,
            empty_change_events_after: bool = False,
    ):
        self.expected_restaurant_status = expected_restaurant_status
        self.empty_change_events_after = empty_change_events_after

    async def check_after(self):
        expected_order = copy.deepcopy(self.initial_order)
        expected_order['status'][
            'restaurant_status'
        ] = self.expected_restaurant_status

        if expected_order['status'] != self.initial_order['status']:
            expected_order['status_history'].append(expected_order['status'])

        await self._check_order(
            expected_order,
            empty_change_events_after=self.empty_change_events_after,
        )


class DbOrderIsChangedByTransactions(DbChecker):
    def __init__(
            self,
            expected_invoice_status: str,
            expected_restaurant_status: Optional[str] = None,
            empty_change_events_after: bool = False,
    ):
        self.expected_invoice_status = expected_invoice_status
        self.expected_restaurant_status = expected_restaurant_status
        self.empty_change_events_after = empty_change_events_after

    async def check_after(self):
        expected_order = copy.deepcopy(self.initial_order)
        expected_order['status'][
            'invoice_status'
        ] = self.expected_invoice_status
        if self.expected_restaurant_status:
            expected_order['status'][
                'restaurant_status'
            ] = self.expected_restaurant_status
        if expected_order['status'] != self.initial_order['status']:
            expected_order['status_history'].append(expected_order['status'])

        await self._check_order(
            expected_order,
            empty_change_events_after=self.empty_change_events_after,
        )


@dataclasses.dataclass
class OrderUserUpdateData:
    invoice_status: str
    locale: str
    user_id: str
    yandex_uid: str
    invoice_id: str
    payment_method_type: str
    personal_email_id: Optional[str]
    payment_method_id: str
    complement_payment_method_type: Optional[str] = None
    complement_payment_method_id: Optional[str] = None
    complement_balance: Optional[str] = None


class DbOrderIsChangedByUser(DbChecker):
    def __init__(
            self,
            user_update_data: OrderUserUpdateData,
            item_complement_amounts: Optional[List[str]] = None,
            total_complement_amount: Optional[str] = None,
    ):
        self.user_update_data = user_update_data
        self.item_complement_amounts = item_complement_amounts
        self.total_complement_amount = total_complement_amount

    async def check_after(self):
        expected_order = copy.deepcopy(self.initial_order)
        expected_order['status'][
            'invoice_status'
        ] = self.user_update_data.invoice_status
        expected_order['invoice_id'] = self.user_update_data.invoice_id
        expected_order['yandex_uid'] = self.user_update_data.yandex_uid
        expected_order['user_id'] = self.user_update_data.user_id
        expected_order[
            'payment_method_type'
        ] = self.user_update_data.payment_method_type
        expected_order[
            'payment_method_id'
        ] = self.user_update_data.payment_method_id
        expected_order['locale'] = self.user_update_data.locale
        expected_order['version'] = self.initial_order['version'] + 1

        if self.total_complement_amount:
            expected_order[
                'complement_payment_method_type'
            ] = self.user_update_data.complement_payment_method_type
            expected_order[
                'complement_payment_method_id'
            ] = self.user_update_data.complement_payment_method_id
            expected_order['complement_amount'] = decimal.Decimal(
                self.total_complement_amount,
            )

            for index, complement_amount in enumerate(
                    self.item_complement_amounts,
            ):
                expected_order['items'][index][
                    'complement_amount'
                ] = decimal.Decimal(complement_amount)
        else:
            expected_order['complement_payment_method_type'] = None
            expected_order['complement_payment_method_id'] = None
            expected_order['complement_amount'] = None
            for item in expected_order['items']:
                item['complement_amount'] = None

        if expected_order['status'] != self.initial_order['status']:
            expected_order['status_history'].append(expected_order['status'])
        expected_order[
            'personal_email_id'
        ] = self.user_update_data.personal_email_id

        change_event = {
            'type': 'charge',
            'operation_id': None,
            'items': expected_order['items'],
            'complement_difference': expected_order['complement_amount'],
            'amount_difference': expected_order['total_price'],
            'status': 'pending',
            'version': expected_order['version'],
            'admin_info': None,
        }

        expected_order['changelog'] = [change_event]
        await self._check_order(expected_order)


@dataclasses.dataclass
class StqMockChecker:
    calls: dict
    expected_calls: dict

    def check_calls(self):
        assert self.calls == self.expected_calls


@pytest.fixture(name='mok_stq')
def mock_stq_fixture(mockserver):
    def _mock_stq_fixture(
            order_id: str,
            process_cleared_called: bool = False,
            close_order_called: bool = False,
            restaurant_order_expired: bool = False,
            cancel_order_called: bool = False,
            update_transactions_called: bool = False,
    ):
        invoice_id = f'eda_{order_id}'
        calls = {
            'restaurant_order_update_transactions': 0,
            'restaurant_order_process_cleared': 0,
            'restaurant_order_expired': 0,
            'payments_eda_cancel_order': 0,
            'payments_eda_close_order': 0,
        }
        expected_calls = {
            'restaurant_order_update_transactions': (
                1 if update_transactions_called else 0
            ),
            'restaurant_order_process_cleared': (
                1 if process_cleared_called else 0
            ),
            'restaurant_order_expired': 1 if restaurant_order_expired else 0,
            'payments_eda_cancel_order': 1 if cancel_order_called else 0,
            'payments_eda_close_order': 1 if close_order_called else 0,
        }

        @mockserver.json_handler(
            r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
        )
        async def _queue(request, queue_name):
            assert queue_name in calls
            calls[queue_name] += 1
            assert request.json['task_id'] == invoice_id
            assert request.json['args'] == []
            kwargs = request.json['kwargs']
            if queue_name in [
                    'restaurant_order_process_cleared',
                    'restaurant_order_update_transactions',
            ]:
                assert kwargs == dict(invoice_id=invoice_id)
            elif queue_name == 'restaurant_order_expired':
                assert kwargs['invoice_id'] == invoice_id
                assert (
                    kwargs['restaurant_status'] == 'WAITING_FOR_CONFIRMATION'
                )
                assert kwargs['invoice_status'] in [
                    'HELD',
                    'CLEARED',
                    'CLEARING',
                ]
            else:
                assert kwargs == dict(order_id=invoice_id)

        return StqMockChecker(calls=calls, expected_calls=expected_calls)

    return _mock_stq_fixture


@pytest.fixture(name='test_internal_update')
def test_internal_update_fixture(web_app_client, get_db_order):
    async def _test_update_fixture(
            order_id,
            operation_id,
            new_invoice_status,
            db_checker: Optional[DbChecker] = None,
            expected_response_code=200,
    ):
        invoice_id = f'eda_{order_id}'

        if db_checker:
            await db_checker.init_db_order(
                order_id=order_id, get_db_order=get_db_order,
            )
        params = {'invoice_id': invoice_id}
        if operation_id:
            params['operation_id'] = operation_id
        response = await web_app_client.put(
            '/v1/order/update',
            params=params,
            json={'invoice_status': new_invoice_status},
        )
        assert response.status == expected_response_code
        if db_checker:
            await db_checker.check_after()

    return _test_update_fixture


@pytest.fixture(name='test_internal_authorized_update')
def test_internal_authorized_update_fixture(
        web_app_client, get_db_order, patch,
):
    async def _test_update_fixture(
            order_id,
            update_body: OrderUserUpdateData,
            db_checker: Optional[DbChecker] = None,
            expected_response_code=200,
    ):
        if db_checker:
            await db_checker.init_db_order(
                order_id=order_id, get_db_order=get_db_order,
            )
        params = {'order_id': order_id}
        body = dict(
            invoice_status=update_body.invoice_status,
            locale=update_body.locale,
            user_id=update_body.user_id,
            yandex_uid=update_body.yandex_uid,
            invoice_id=update_body.invoice_id,
            payment_method={
                'type': update_body.payment_method_type,
                'id': update_body.payment_method_id,
            },
            personal_email_id=update_body.personal_email_id,
        )
        if update_body.complement_payment_method_type:
            body['complement_payment_method'] = {
                'type': update_body.complement_payment_method_type,
                'id': update_body.complement_payment_method_id,
                'balance': update_body.complement_balance,
            }
        response = await web_app_client.put(
            '/v1/order/authorized-update', params=params, json=body,
        )
        assert response.status == expected_response_code
        if db_checker:
            await db_checker.check_after()

    return _test_update_fixture


@pytest.fixture(name='test_external_update')
def test_external_update_fixture(web_app_client, get_db_order):
    async def _test_external_update_fixture(
            order_id,
            new_restaurant_status,
            db_checker: Optional[DbChecker] = None,
            expected_response_code=200,
    ):
        if db_checker:
            await db_checker.init_db_order(
                order_id=order_id, get_db_order=get_db_order,
            )
        response = await web_app_client.put(
            '/external/v1/order/status',
            headers={'X-YaTaxi-Api-Key': stubs.ApiKey.RESTAURANT_01},
            params={'order_id': order_id},
            json={'status': new_restaurant_status},
        )
        assert response.status == expected_response_code
        if db_checker:
            await db_checker.check_after()

    return _test_external_update_fixture


# order/update should work even when IIKO_INTEGRATION_SERVICE_AVAILABLE=False
@pytest.mark.config(
    IIKO_INTEGRATION_SERVICE_AVAILABLE=False,
    IIKO_INTEGRATION_USER_NOTIFICATION_BY_STATUS=(
        stubs.CONFIG_USER_NOTIFICATION_BY_STATUS
    ),
    IIKO_INTEGRATION_RESTAURANT_INFO=stubs.CONFIG_RESTAURANT_INFO,
    IIKO_INTEGRATION_RESTAURANT_GROUP_INFO=stubs.CONFIG_RESTAURANT_GROUP_INFO,
)
@pytest.mark.now('2020-02-25T18:50:00')
@pytest.mark.parametrize('order_id, operation_id, case', all_cases_params())
async def test_order_internal_update(
        mok_stq,
        test_internal_update,
        operation_id: Optional[str],
        order_id: str,
        case: InvoiceTransitionCase,
):
    stq_calls = {}
    db_checker: Optional[DbChecker] = None

    if case.response_code == 200:
        changed_restaurant_status: Optional[str] = None
        if case.changed_restaurant_status:
            changed_restaurant_status = case.changed_restaurant_status
        db_checker = DbOrderIsChangedByTransactions(
            expected_invoice_status=case.new_status,
            expected_restaurant_status=changed_restaurant_status,
            empty_change_events_after=case.empty_change_events_after,
        )
    elif case.response_code != 404:
        db_checker = DbOrderIsNotChanged()
    if case.stq_calls:
        for stq_call in case.stq_calls:
            stq_calls[stq_call] = True

    stq_mock_checker = mok_stq(order_id=order_id, **stq_calls)
    await test_internal_update(
        order_id=order_id,
        operation_id=operation_id,
        new_invoice_status=case.new_status,
        db_checker=db_checker,
        expected_response_code=case.response_code,
    )
    stq_mock_checker.check_calls()

    if case.response_code == 200:
        stq_mock_checker = mok_stq(order_id=order_id, **stq_calls)
        await test_internal_update(
            order_id=order_id,
            operation_id=operation_id,
            new_invoice_status=case.new_status,
            db_checker=DbOrderIsNotChanged(),
            expected_response_code=case.response_code,
        )
        stq_mock_checker.check_calls()


# order/update should work even when IIKO_INTEGRATION_SERVICE_AVAILABLE=False
@pytest.mark.config(
    IIKO_INTEGRATION_SERVICE_AVAILABLE=False,
    IIKO_INTEGRATION_ORDER_STATUS_POLLING_DELAY=3,
    **stubs.RESTAURANT_INFO_CONFIGS,
    IIKO_INTEGRATION_USER_NOTIFICATION_BY_STATUS=(
        stubs.CONFIG_USER_NOTIFICATION_BY_STATUS
    ),
)
@pytest.mark.now('2020-02-25T18:50:00')
@pytest.mark.parametrize(
    'order_id,  case', all_cases_params(is_restaurant=True),
)
async def test_order_external_update(
        test_external_update,
        mok_stq,
        order_id: str,
        case: RestaurantTransitionCase,
):
    stq_calls = {}
    db_checker: Optional[DbChecker] = None
    if case.response_code == 200:
        db_checker = DbOrderIsChangedByRestaurant(
            expected_restaurant_status=case.new_status,
            empty_change_events_after=case.empty_change_events_after,
        )
    elif case.response_code != 404:
        db_checker = DbOrderIsNotChanged()

    if case.stq_calls:
        for stq_call in case.stq_calls:
            stq_calls[stq_call] = True

    stq_mock_checker = mok_stq(order_id=order_id, **stq_calls)
    await test_external_update(
        order_id=order_id,
        new_restaurant_status=case.new_status,
        db_checker=db_checker,
        expected_response_code=case.response_code,
    )
    stq_mock_checker.check_calls()

    if case.response_code == 200:
        stq_mock_checker = mok_stq(order_id=order_id, **stq_calls)
        await test_external_update(
            order_id=order_id,
            new_restaurant_status=case.new_status,
            db_checker=DbOrderIsNotChanged(),
            expected_response_code=case.response_code,
        )
        stq_mock_checker.check_calls()


USER_UPDATE_BODY_HOLDING = OrderUserUpdateData(
    invoice_id='new_invoice',
    invoice_status='HOLDING',
    locale='lo',
    user_id='new_user',
    yandex_uid='new_yandex',
    payment_method_type='card',
    payment_method_id='card-123',
    personal_email_id=None,
)

UPDATE_BODY_WITH_EMAIL_ID = OrderUserUpdateData(
    invoice_id='new_invoice',
    invoice_status='HOLDING',
    locale='lo',
    user_id='new_user',
    yandex_uid='new_yandex',
    payment_method_type='card',
    payment_method_id='card-123',
    personal_email_id='123455dab2323bd785a',
)


USER_UPDATE_BODY_HELD = OrderUserUpdateData(
    invoice_id='new_invoice',
    invoice_status='HELD',
    locale='lo',
    user_id='new_user',
    yandex_uid='new_yandex',
    payment_method_type='card',
    payment_method_id='card-123',
    personal_email_id=None,
)


def user_update_body_complement(complement_balance: str):
    return OrderUserUpdateData(
        invoice_id='new_invoice',
        invoice_status='HOLDING',
        locale='lo',
        user_id='new_user',
        yandex_uid='new_yandex',
        payment_method_type='card',
        payment_method_id='card-123',
        complement_payment_method_type='personal_wallet',
        complement_payment_method_id='personal_wallet-123',
        complement_balance=complement_balance,
        personal_email_id='personal_email_id',
    )


@pytest.mark.config(IIKO_INTEGRATION_SERVICE_AVAILABLE=False)
@pytest.mark.now('2020-02-25T18:50:00')
@pytest.mark.parametrize(
    [
        'order_id',
        'update_body',
        'item_complement_amounts',
        'total_complement_amount',
        'expected_code',
    ],
    [
        # From PENDING, INIT
        pytest.param(
            '21',
            USER_UPDATE_BODY_HOLDING,
            None,
            None,
            200,
            id='OK: no complement payment',
        ),
        pytest.param(
            '21',
            user_update_body_complement(complement_balance='0'),
            None,
            None,
            200,
            id='OK: complement_amount=10',
        ),
        pytest.param(
            '21',
            user_update_body_complement(complement_balance='10'),
            ['10', '0', '0'],
            '10',
            200,
            id='OK: complement_amount=10',
        ),
        pytest.param(
            '21',
            user_update_body_complement(complement_balance='150'),
            ['149', '1', '0'],
            '150',
            200,
            id='OK: no complement payment',
        ),
        pytest.param(
            '21',
            user_update_body_complement(complement_balance='300'),
            ['149', '99', '49'],
            '297',
            200,
            id='OK: no complement payment',
        ),
        pytest.param(
            '21',
            UPDATE_BODY_WITH_EMAIL_ID,
            None,
            None,
            200,
            id='personal_email_id in request',
        ),
        pytest.param(
            'not_exist',
            USER_UPDATE_BODY_HOLDING,
            None,
            None,
            404,
            id='Not found',
        ),
        # From 'PENDING', 'HOLDING'
        pytest.param(
            '21.1',
            USER_UPDATE_BODY_HOLDING,
            None,
            None,
            409,
            id='Wrong state',
        ),
        pytest.param(
            '21.1',
            USER_UPDATE_BODY_HELD,
            None,
            None,
            409,
            id='Can not updated payment data',
        ),
    ],
)
async def test_order_authorized_update(
        test_internal_authorized_update,
        mok_stq,
        order_id: str,
        update_body: OrderUserUpdateData,
        item_complement_amounts,
        total_complement_amount,
        expected_code: int,
):
    db_checker: Optional[DbChecker] = None
    if expected_code == 200:
        db_checker = DbOrderIsChangedByUser(
            user_update_data=update_body,
            item_complement_amounts=item_complement_amounts,
            total_complement_amount=total_complement_amount,
        )
    elif expected_code != 404:
        db_checker = DbOrderIsNotChanged()

    stq_mock_checker = mok_stq(order_id=order_id)
    await test_internal_authorized_update(
        order_id=order_id,
        update_body=update_body,
        db_checker=db_checker,
        expected_response_code=expected_code,
    )
    stq_mock_checker.check_calls()

    if expected_code == 200:
        stq_mock_checker2 = mok_stq(order_id=order_id)
        await test_internal_authorized_update(
            order_id=order_id,
            update_body=update_body,
            db_checker=DbOrderIsNotChanged(),
            expected_response_code=expected_code,
        )
        stq_mock_checker2.check_calls()


# order/update should work even when IIKO_INTEGRATION_SERVICE_AVAILABLE=False
@pytest.mark.config(
    IIKO_INTEGRATION_SERVICE_AVAILABLE=False,
    IIKO_INTEGRATION_USER_NOTIFICATION_BY_STATUS=(
        # Notifying statuses: HELD_AND_CONFIRMED, HOLD_FAILED,
        # CLOSED_BY_RESTAURANT, CANCELED_BY_RESTAURANT
        stubs.CONFIG_USER_NOTIFICATION_BY_STATUS
    ),
    IIKO_INTEGRATION_RESTAURANT_INFO=stubs.CONFIG_RESTAURANT_INFO,
    IIKO_INTEGRATION_RESTAURANT_GROUP_INFO=stubs.CONFIG_RESTAURANT_GROUP_INFO,
)
@pytest.mark.parametrize(
    [
        'new_invoice_status',
        'new_restaurant_status',
        'order_id',
        'response_code',
        'user_notified',
    ],
    [
        # From PENDING, HOLDING w/o locale
        pytest.param('HELD', None, '13', 200, True),
        pytest.param('HOLD_FAILED', None, '13', 200, True),
        # From PENDING, HOLDING
        pytest.param('HELD', None, '14', 200, True),
        pytest.param('HOLD_FAILED', None, '14', 200, True),
        # From PAYMENT_CONFIRMED, HELD
        pytest.param('CLEARING', None, '07', 200, False),
        pytest.param('HELD', None, '07', 200, False),
        # From PAYMENT_CONFIRMED, HELD
        pytest.param('HELD', None, '07', 200, False),
        # from PENDING, HOLDING
        pytest.param(None, 'CANCELED', '11.1', 200, True),
        pytest.param(None, 'CLOSED', '11.1', 200, True),
        # from 'PENDING', 'INIT' w/o user
        pytest.param(None, 'CANCELED', '21', 200, False),
        pytest.param(None, 'CLOSED', '21', 200, False),
    ],
)
async def test_notification(
        test_internal_update,
        test_external_update,
        get_db_order,
        mockserver,
        wait_for_ucommunications_task,
        new_invoice_status: Optional[str],
        new_restaurant_status: Optional[str],
        order_id: str,
        response_code: int,
        user_notified: bool,
):
    db_order = await get_db_order(fields='*', id=order_id)
    locale = db_order['locale']
    user_id = db_order['user_id']

    r_status = new_restaurant_status or db_order['status']['restaurant_status']
    i_status = new_invoice_status or db_order['status']['invoice_status']
    full_status = f'{r_status}+{i_status}'
    # mapping from statuses to combined status, based on config from stubs
    notification_keys = {}
    for status in ALL_INVOICE_STATUSES:
        # according to config, these are valid for all invoce statuses
        notification_keys[('CLOSED', status)] = 'CLOSED+'
        notification_keys[('CANCELED', status)] = 'CANCELED+'

    key = notification_keys.get((r_status, i_status), full_status)
    expected_notification = stubs.CONFIG_USER_NOTIFICATION_BY_STATUS.get(key)

    class UcommunicationContext:
        idempotency_token = None

    ucommunication_context = UcommunicationContext()

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def _ucommunications_mock(req):
        assert 'X-Idempotency-Token' in req.headers
        ucommunication_context.idempotency_token = req.headers[
            'X-Idempotency-Token'
        ]
        assert req.json == {
            'intent': expected_notification['intent'],
            'locale': locale or const.DEFAULT_LOCALE,
            'text': {
                'key': expected_notification['tanker_key'],
                'keyset': 'notify',
            },
            'user_id': user_id,
        }
        return {'code': 'code', 'message': 'message'}

    if new_invoice_status:
        await test_internal_update(
            order_id=order_id,
            operation_id=None,
            new_invoice_status=new_invoice_status,
            expected_response_code=response_code,
        )
    else:
        await test_external_update(
            order_id=order_id,
            new_restaurant_status=new_restaurant_status,
            expected_response_code=response_code,
        )
    await wait_for_ucommunications_task()

    if user_notified:
        assert _ucommunications_mock.times_called == 1
    else:
        assert _ucommunications_mock.times_called == 0

    if user_notified:
        idempotency_token1 = ucommunication_context.idempotency_token
        if new_invoice_status:
            await test_internal_update(
                order_id=order_id,
                operation_id=None,
                new_invoice_status=new_invoice_status,
                expected_response_code=response_code,
            )
        else:
            await test_external_update(
                order_id=order_id,
                new_restaurant_status=new_restaurant_status,
                expected_response_code=response_code,
            )
        await wait_for_ucommunications_task()
        assert _ucommunications_mock.times_called == 2
        idempotency_token2 = ucommunication_context.idempotency_token
        assert idempotency_token1 == idempotency_token2
