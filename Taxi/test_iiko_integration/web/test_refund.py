import copy
import dataclasses
import datetime
import decimal
from typing import List
from typing import Optional

import pytest

from iiko_integration.data_access import orders_db
from iiko_integration.data_access import utils as db_utils
from iiko_integration.model import order as order_model


ORDER_FIELDS = ['changelog', 'items', 'version', 'total_price', 'discount']

NOW = datetime.datetime(2042, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.now(NOW.isoformat()),
    pytest.mark.config(
        QR_PAY_REFUND_AVAILABLE_REASONS={'reason_code': 'reason_description'},
    ),
]


def _item(
        item_id: int,
        quantity: str,
        price_per_unit: str,
        price_without_discount: str,
        price_for_customer: str,
        discount_amount: str,
        discount_percent: str,
        vat_amount: str,
        vat_percent: str,
        name: str,
        complement_amount: Optional[str] = None,
):
    return dict(
        item_id=item_id,
        product_id=f'0{item_id}',
        parent_product_id=None,
        name=name,
        quantity=decimal.Decimal(quantity),
        price_per_unit=decimal.Decimal(price_per_unit),
        price_without_discount=decimal.Decimal(price_without_discount),
        price_for_customer=decimal.Decimal(price_for_customer),
        discount_amount=decimal.Decimal(discount_amount),
        discount_percent=decimal.Decimal(discount_percent),
        vat_amount=decimal.Decimal(vat_amount),
        vat_percent=decimal.Decimal(vat_percent),
        complement_amount=decimal.Decimal(complement_amount)
        if complement_amount
        else None,
    )


DB_4ITEMS = [
    _item(
        1, '3', '50', '150', '150', '0', '0', '25', '20', 'Hamburger', '149',
    ),
    _item(2, '0.5', '250', '125', '100', '25', '20', '0', '0', 'Cola', '50'),
    _item(
        3, '0.5', '100', '50', '50', '0', '0', '0', '0', 'French_fries', '0',
    ),
    _item(4, '1', '0', '0', '0', '0', '0', '0', '0', 'Air', '0'),
]


def item_changes(item_id: int, **kwargs):
    item = copy.deepcopy(DB_4ITEMS[item_id - 1])
    for key, value in kwargs.items():
        if value is not None:
            item[key] = type(item[key])(value)
        else:
            item[key] = None
    return item


def item_full_refund_changes(item_id):
    return item_changes(
        item_id,
        quantity='0',
        price_without_discount='0',
        price_for_customer='0',
        discount_amount='0',
        vat_amount='0',
        complement_amount='0',
    )


def changed_items_composite(*args):
    result = copy.deepcopy(DB_4ITEMS)
    for item in args:
        result[item['item_id'] - 1] = item
    return result


def changed_items(*args):
    items = changed_items_composite(*args)
    for item in items:
        item['complement_amount'] = None
    return items


class DBChecker:

    # pylint: disable=attribute-defined-outside-init
    async def init_db_order(self, order_id, get_db_order):
        self.get_db_order = get_db_order
        self.order_id = order_id
        self.initial_order = await get_db_order(
            fields=ORDER_FIELDS, id=order_id,
        )

    async def check_after_request(self):
        pass

    async def _check_order(self, expected_order):
        order = await self.get_db_order(fields=ORDER_FIELDS, id=self.order_id)
        if order:
            for index, change_event in enumerate(expected_order['changelog']):
                change_event['created_at'] = order['changelog'][index][
                    'created_at'
                ]
                change_event['updated_at'] = order['changelog'][index][
                    'updated_at'
                ]
        assert order == expected_order


class DBCheckerOrderIsNotChanged(DBChecker):
    async def check_after_request(self):
        await self._check_order(self.initial_order)


class DBCheckerOrderIsChanged(DBChecker):
    def __init__(
            self,
            expected_items: list,
            expected_total_price: str,
            expected_discount: str,
            expected_complement_difference: Optional[str] = None,
    ):
        self.expected_items = expected_items
        self.expected_total_price = decimal.Decimal(expected_total_price)
        self.expected_discount = decimal.Decimal(expected_discount)
        self.expected_complement_difference = (
            decimal.Decimal(expected_complement_difference)
            if expected_complement_difference
            else None
        )

    async def check_after_request(self):
        expected_version = self.initial_order['version'] + 1
        expetcted_amount_difference = (
            self.expected_total_price - self.initial_order['total_price']
        )
        new_event = {
            'items': self.expected_items,
            'created_at': NOW,
            'updated_at': NOW,
            'amount_difference': expetcted_amount_difference,
            'complement_difference': self.expected_complement_difference,
            'version': expected_version,
            'status': 'pending',
            'type': 'refund',
            'operation_id': None,
            'admin_info': {
                'operator_login': 'yandex_login',
                'reason_code': 'reason_code',
                'ticket': 'TAXITICKET-1',
                'ticket_type': 'startrack',
            },
        }
        expected_order = {
            'version': expected_version,
            'items': self.expected_items,
            'total_price': self.expected_total_price,
            'discount': self.expected_discount,
            'changelog': [*self.initial_order['changelog'], new_event],
        }

        await self._check_order(expected_order)


@pytest.fixture(name='test_refund')
def test_refund_fixture(web_app_client, stq, get_db_order):
    async def _test_refund_fixture(
            order_id,
            request_data,
            expected_code,
            expected_invoice_id,
            db_checker,
    ):
        await db_checker.init_db_order(
            order_id=order_id, get_db_order=get_db_order,
        )

        request_data = {
            'version': 1,
            'reason_code': 'reason_code',
            'ticket': {'ticket': 'TAXITICKET-1', 'type': 'startrack'},
            **request_data,
        }
        response = await web_app_client.post(
            f'/admin/qr-pay/v1/order/refund?id={order_id}',
            json=request_data,
            headers={'X-Yandex-Login': 'yandex_login'},
        )
        assert response.status == expected_code

        if expected_code == 200:
            assert stq.restaurant_order_update_transactions.times_called == 1
            task = stq.restaurant_order_update_transactions.next_call()
            assert task['kwargs']['invoice_id'] == expected_invoice_id
        else:
            assert stq.restaurant_order_update_transactions.times_called == 0

        await db_checker.check_after_request()

    return _test_refund_fixture


@pytest.mark.parametrize(
    ('order', 'request_data', 'db_checker', 'expected_code'),
    [
        pytest.param(
            '4items_cleared',
            {'items': [{'item_id': 2, 'quantity': '0.5'}], 'version': 1},
            DBCheckerOrderIsChanged(
                expected_items=changed_items(item_full_refund_changes(2)),
                expected_total_price='200',
                expected_discount='0',
            ),
            200,
            id='full_refund_one_position',
        ),
        pytest.param(
            '4items_cleared_composite',
            {'items': [{'item_id': 2, 'quantity': '0.5'}], 'version': 1},
            DBCheckerOrderIsChanged(
                expected_items=changed_items_composite(
                    item_full_refund_changes(2),
                ),
                expected_total_price='200',
                expected_discount='0',
                expected_complement_difference='-50',
            ),
            200,
            id='full_refund_one_composite_position',
        ),
        pytest.param(
            '4items_refunding',
            {
                'items': [
                    {'item_id': 1, 'quantity': '3'},
                    {'item_id': 2, 'quantity': '0.1'},
                    {'item_id': 3, 'quantity': '0.5'},
                    {'item_id': 4, 'quantity': '1'},
                ],
                'version': 2,
            },
            DBCheckerOrderIsChanged(
                expected_items=changed_items(
                    item_full_refund_changes(1),
                    item_full_refund_changes(2),
                    item_full_refund_changes(3),
                    item_full_refund_changes(4),
                ),
                expected_total_price='0',
                expected_discount='0',
            ),
            200,
            id='full_refund_all_position',
        ),
        pytest.param(
            '4items_cleared_composite',
            {
                'items': [
                    {'item_id': 1, 'quantity': '3'},
                    {'item_id': 2, 'quantity': '0.5'},
                    {'item_id': 3, 'quantity': '0.5'},
                    {'item_id': 4, 'quantity': '1'},
                ],
                'version': 1,
            },
            DBCheckerOrderIsChanged(
                expected_items=changed_items_composite(
                    item_full_refund_changes(1),
                    item_full_refund_changes(2),
                    item_full_refund_changes(3),
                    item_full_refund_changes(4),
                ),
                expected_total_price='0',
                expected_discount='0',
                expected_complement_difference='-199',
            ),
            200,
            id='full_refund_all_composite_position',
        ),
        pytest.param(
            '4items_cleared',
            {
                'items': [
                    {'item_id': 1, 'quantity': '2'},
                    {'item_id': 2, 'quantity': '0.4'},
                    {'item_id': 3, 'quantity': '0.4'},
                ],
                'version': 1,
            },
            DBCheckerOrderIsChanged(
                expected_items=changed_items(
                    item_changes(
                        1,
                        quantity='1',
                        price_without_discount='50',
                        price_for_customer='50',
                        vat_amount='8.333333333333333333333333333',
                    ),
                    item_changes(
                        2,
                        quantity='0.1',
                        price_without_discount='25.0',
                        price_for_customer='20.0',
                        discount_amount='5.0',
                        vat_amount='0.0',
                    ),
                    item_changes(
                        3,
                        quantity='0.1',
                        price_without_discount='10.0',
                        price_for_customer='10.0',
                        discount_amount='0',
                        vat_amount='0.0',
                    ),
                ),
                expected_total_price='80',
                expected_discount='5.0',
            ),
            200,
            id='partial_refund_several_position',
        ),
        pytest.param(
            '4items_cleared_composite',
            {
                'items': [
                    {'item_id': 1, 'quantity': '2'},
                    {'item_id': 2, 'quantity': '0.4'},
                    {'item_id': 3, 'quantity': '0.4'},
                ],
                'version': 1,
            },
            DBCheckerOrderIsChanged(
                expected_items=changed_items_composite(
                    item_changes(
                        1,
                        quantity='1',
                        price_without_discount='50',
                        price_for_customer='50',
                        vat_amount='8.333333333333333333333333333',
                        complement_amount='49',
                    ),
                    item_changes(
                        2,
                        quantity='0.1',
                        price_without_discount='25.0',
                        price_for_customer='20.0',
                        discount_amount='5.0',
                        vat_amount='0.0',
                        complement_amount='0',
                    ),
                    item_changes(
                        3,
                        quantity='0.1',
                        price_without_discount='10.0',
                        price_for_customer='10.0',
                        discount_amount='0',
                        vat_amount='0.0',
                        complement_amount='0',
                    ),
                ),
                expected_total_price='80',
                expected_discount='5.0',
                expected_complement_difference='-150',
            ),
            200,
            id='partial_refund_several_composite_positions',
        ),
        pytest.param(
            '4items_refunding',
            {'items': [{'item_id': 1, 'quantity': '1'}], 'version': 1},
            DBCheckerOrderIsNotChanged(),
            409,
            id='version_mismatch',
        ),
        pytest.param(
            '4items_cleared_composite',
            {
                'items': [
                    {'item_id': 1, 'quantity': '1'},
                    {'item_id': 42, 'quantity': '1'},
                ],
                'version': 1,
            },
            DBCheckerOrderIsNotChanged(),
            400,
            id='nonexistent_item_id',
        ),
        pytest.param(
            '4items_cleared_composite',
            {
                'items': [
                    {'item_id': 1, 'quantity': '1'},
                    {'item_id': 1, 'quantity': '2'},
                ],
                'version': 1,
            },
            DBCheckerOrderIsNotChanged(),
            400,
            id='duplicated_item_id',
        ),
        pytest.param(
            '4items_cleared_composite',
            {
                'items': [
                    {'item_id': 1, 'quantity': '-1'},
                    {'item_id': 2, 'quantity': '-0.6'},
                ],
                'version': 1,
            },
            DBCheckerOrderIsNotChanged(),
            400,
            id='negative_quantity',
        ),
        pytest.param(
            '4items_cleared_composite',
            {
                'items': [{'item_id': 1, 'quantity': '1'}],
                'version': 1,
                'reason_code': 'unavailable_reason',
            },
            DBCheckerOrderIsNotChanged(),
            400,
            id='unavailable_reason',
        ),
        pytest.param(
            'bad_items_cleared',
            {'items': [{'item_id': 2, 'quantity': '0.4'}], 'version': 1},
            DBCheckerOrderIsNotChanged(),
            400,
            id='bad_items',
        ),
    ],
)
async def test_refund_main_cases(
        test_refund,
        order: str,
        request_data: dict,
        expected_code: int,
        db_checker: DBChecker,
):
    await test_refund(
        order_id=f'order_{order}',
        request_data=request_data,
        expected_code=expected_code,
        expected_invoice_id=f'invoice_{order}',
        db_checker=db_checker,
    )


async def test_version_mismatch_while_updating_db(test_refund, monkeypatch):
    order = '4items_refunding'
    request_data = {'items': [{'item_id': 2, 'quantity': '0'}], 'version': 2}
    expected_code = 409

    # pylint: disable=protected-access
    async def push_changes_patched(
            self,
            current_order: order_model.Order,
            new_version: int,
            new_items: List[order_model.OrderItem],
            admin_info: Optional[order_model.AdminInfo] = None,
    ):
        current_order.version -= 1
        new_total_price = order_model.calc_total_price(new_items)
        new_discount = order_model.calc_total_discount(new_items)
        amount_difference = new_total_price - current_order.total_price
        event_type = order_model.ChangeType.REFUND.value
        admin_info_dict = None
        new_items_dict = [dataclasses.asdict(item) for item in new_items]
        query, query_args = self.sqlt.order_push_changes(
            order_id=current_order.id,
            current_version=current_order.version,
            new_version=new_version,
            new_items=new_items_dict,
            new_total_price=new_total_price,
            new_discount=new_discount,
            new_event_amount_difference=amount_difference,
            new_event_status=order_model.ChangeStatus.PENDING.value,
            new_event_operation_id=None,
            new_event_admin_info=admin_info_dict,
            new_event_type=event_type,
            new_complement_amount=None,
            new_event_complement_difference=None,
        )
        not_found_details = (
            f'order_id={current_order.id}, version={current_order.version}'
        )
        order_raw = await self._fetch_order_and_update(
            query=query,
            query_args=query_args,
            not_found_error_details=not_found_details,
        )
        return db_utils.to_order(order_raw)

    monkeypatch.setattr(
        orders_db.OrdersDb, 'push_changes', push_changes_patched,
    )

    await test_refund(
        order_id=f'order_{order}',
        request_data=request_data,
        expected_code=expected_code,
        expected_invoice_id=f'invoice_{order}',
        db_checker=DBCheckerOrderIsNotChanged(),
    )


@pytest.mark.config(
    QR_PAY_REFUND_AVAILABLE_REASONS={'reason_code': 'reason_description'},
)
@pytest.mark.parametrize(
    ('order', 'expected_code'),
    (
        ('pending', 409),
        ('canceled', 409),
        ('closed', 409),
        ('holding', 409),
        ('held_and_waiting', 409),
        ('hold_failed', 409),
        ('held_and_confirmed', 200),
        ('clearing', 200),
        ('cleared', 200),
        ('refunding', 200),
        ('nonexistent', 404),
    ),
)
async def test_order_state(test_refund, order: str, expected_code: int):
    request_data = {'items': [{'item_id': 1, 'quantity': '3'}], 'version': 1}
    if expected_code == 200:
        db_checker: DBChecker = DBCheckerOrderIsChanged(
            expected_items=[
                _item(
                    1, '0', '50', '0', '0', '0', '0', '0', '20', 'Hamburger',
                ),
            ],
            expected_total_price='0',
            expected_discount='0',
        )
    else:
        db_checker = DBCheckerOrderIsNotChanged()
    await test_refund(
        order_id=f'order_{order}',
        request_data=request_data,
        expected_code=expected_code,
        expected_invoice_id=f'invoice_{order}',
        db_checker=db_checker,
    )
