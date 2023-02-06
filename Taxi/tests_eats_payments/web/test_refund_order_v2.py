import typing

import pytest

from tests_eats_payments import configs
from tests_eats_payments import consts
from tests_eats_payments import db_order
from tests_eats_payments import helpers
from tests_eats_payments import models

URL = 'v2/orders/refund'

OPERATION_ID = 'refund:abcd'
ORDER_ID = 'test_order'

COMPLEMENT = models.Complement(amount='1.00')

BASE_PAYLOAD = {'order_id': ORDER_ID, 'version': 2, 'revision': 'abcd'}


@pytest.fixture(name='mock_refund_invoice_retrieve')
def _mock_refund_invoice_retrieve(mock_transactions_invoice_retrieve):
    def _inner(
            *args, invoice_status: typing.Optional[str] = 'cleared', **kwargs,
    ):
        return mock_transactions_invoice_retrieve(
            status=invoice_status, *args, **kwargs,
        )

    return _inner


@pytest.fixture(name='check_refund')
def check_refund_fixture(taxi_eats_payments, mockserver, load_json):
    async def _inner(response_status=200, response_body=None):
        payload: typing.Dict[str, typing.Any] = {**BASE_PAYLOAD}
        response = await taxi_eats_payments.post(URL, json=payload)
        assert response.status == response_status
        if response_body is not None:
            assert response.json() == response_body

    return _inner


@configs.PERSONAL_WALLET_FIRM_BY_SERVICE
@pytest.mark.parametrize(
    [
        'customer_services',
        'invoice_retrieve_items',
        'invoice_update_items',
        'wallet_refund',
    ],
    [
        pytest.param(
            [
                helpers.make_customer_service(
                    customer_service_id='composition-products-0',
                    name='Composition products',
                    cost_for_customer='1.00',
                    currency='RUB',
                    customer_service_type='retail',
                    vat='nds_18',
                    trust_product_id='burger',
                    place_id='place_1',
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products-0', amount='2.00',
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products-0', amount='1.00',
                        ),
                    ],
                ),
            ],
            None,
            id=(
                'Test with a partial refund for a single item'
                ' and a single payment type'
            ),
        ),
        pytest.param(
            [
                helpers.make_customer_service(
                    customer_service_id='composition-products-0',
                    name='Composition products',
                    cost_for_customer='0.00',
                    currency='RUB',
                    customer_service_type='retail',
                    vat='nds_18',
                    trust_product_id='burger',
                    place_id='place_1',
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products-0', amount='2.00',
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products-0', amount='0.00',
                        ),
                    ],
                ),
            ],
            None,
            id=(
                'Test with a full refund for a single item'
                ' and a single payment type'
            ),
        ),
        pytest.param(
            [
                helpers.make_customer_service(
                    customer_service_id='composition-products-0',
                    name='Composition products',
                    cost_for_customer='0.00',
                    currency='RUB',
                    customer_service_type='retail',
                    vat='nds_18',
                    trust_product_id='burger',
                    place_id='place_1',
                ),
                helpers.make_customer_service(
                    customer_service_id='delivery-0',
                    name='Delivery',
                    cost_for_customer='3.00',
                    currency='RUB',
                    customer_service_type='delivery',
                    vat='nds_18',
                    trust_product_id='burger',
                    place_id='place_1',
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products-0', amount='20.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='delivery-0', amount='5.00',
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products-0', amount='0.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='delivery-0', amount='3.00',
                        ),
                    ],
                ),
            ],
            None,
            id=(
                'Test with a partial refund for multiple items'
                ' and a single payment type'
            ),
        ),
        pytest.param(
            [
                helpers.make_customer_service(
                    customer_service_id='composition-products-0',
                    name='Composition products',
                    cost_for_customer='0.00',
                    currency='RUB',
                    customer_service_type='retail',
                    vat='nds_18',
                    trust_product_id='burger',
                    place_id='place_1',
                ),
                helpers.make_customer_service(
                    customer_service_id='delivery-0',
                    name='Delivery',
                    cost_for_customer='0.00',
                    currency='RUB',
                    customer_service_type='delivery',
                    vat='nds_18',
                    trust_product_id='burger',
                    place_id='place_1',
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products-0', amount='20.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='delivery-0', amount='5.00',
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products-0', amount='0.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='delivery-0', amount='0.00',
                        ),
                    ],
                ),
            ],
            None,
            id=(
                'Test with a full refund for multiple items'
                ' and a single payment type, some items remaining'
            ),
        ),
        pytest.param(
            [
                helpers.make_customer_service(
                    customer_service_id='composition-products-0',
                    name='Composition products',
                    cost_for_customer='2.00',
                    currency='RUB',
                    customer_service_type='retail',
                    vat='nds_18',
                    trust_product_id='burger',
                    place_id='place_1',
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products-0', amount='2.00',
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='personal_wallet',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products-0', amount='2.00',
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products-0', amount='1.00',
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='personal_wallet',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products-0', amount='1.00',
                        ),
                    ],
                ),
            ],
            '1.00',
            id=(
                'Test with a partial refund for a single item'
                ' and multiple payment types'
            ),
        ),
        pytest.param(
            [
                helpers.make_customer_service(
                    customer_service_id='composition-products-0',
                    name='Composition products 0',
                    cost_for_customer='0.00',
                    currency='RUB',
                    customer_service_type='retail',
                    vat='nds_18',
                    trust_product_id='burger',
                    place_id='place_1',
                ),
                helpers.make_customer_service(
                    customer_service_id='composition-products-1',
                    name='Composition products 1',
                    cost_for_customer='0.00',
                    currency='RUB',
                    customer_service_type='retail',
                    vat='nds_18',
                    trust_product_id='burger',
                    place_id='place_1',
                ),
                helpers.make_customer_service(
                    customer_service_id='composition-products-2',
                    name='Composition products 2',
                    cost_for_customer='3.00',
                    currency='RUB',
                    customer_service_type='retail',
                    vat='nds_18',
                    trust_product_id='burger',
                    place_id='place_1',
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products-0', amount='1.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='composition-products-1', amount='2.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='composition-products-2', amount='3.00',
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='personal_wallet',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products-0', amount='1.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='composition-products-1', amount='1.00',
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products-0', amount='0.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='composition-products-1', amount='0.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='composition-products-2', amount='3.00',
                        ),
                    ],
                ),
            ],
            None,
            id=(
                'Test with a full refund for multiple items'
                ' and multiple payment types'
            ),
        ),
    ],
)
async def test_refund(
        check_refund,
        experiments3,
        fetch_operation,
        mock_refund_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        mock_order_revision_list,
        pgsql,
        customer_services,
        invoice_retrieve_items,
        invoice_update_items,
        wallet_refund,
):
    experiments3.add_config(**helpers.make_operations_config())

    if wallet_refund is not None:
        order = db_order.DBOrder(
            pgsql=pgsql,
            order_id=ORDER_ID,
            complement_payment_type=COMPLEMENT.payment_type,
            complement_payment_id=COMPLEMENT.payment_id,
            complement_amount=COMPLEMENT.amount,
            api_version=2,
        )
        order.upsert()
    else:
        order = db_order.DBOrder(pgsql=pgsql, order_id=ORDER_ID, api_version=2)
        order.upsert()

    previous_operation_items = [
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='composition-products-0', amount='2.00',
                ),
                helpers.make_transactions_item(
                    item_id='delivery-0', amount='3.00',
                ),
                helpers.make_transactions_item(
                    item_id='assembly-0', amount='3.00',
                ),
            ],
        ),
    ]
    operation1 = helpers.make_operation(
        created='2021-03-06T12:00:00.000000+03:00',
        sum_to_pay=previous_operation_items,
    )
    operation2 = helpers.make_operation(
        created='2021-03-06T13:00:00.000000+03:00',
        sum_to_pay=invoice_retrieve_items,
    )

    invoice_retrieve_mock = mock_refund_invoice_retrieve(
        items=invoice_retrieve_items, operations=[operation1, operation2],
    )
    wallet_payload = (
        helpers.make_wallet_payload(
            cashback_service='eda',
            order_id=ORDER_ID,
            wallet_id=COMPLEMENT.payment_id,
        )
        if wallet_refund is not None
        else None
    )

    complement_payment = None
    if wallet_refund is not None:
        complement_payment = models.Complement(amount=wallet_refund)
    invoice_update_mock = mock_transactions_invoice_update(
        items=invoice_update_items,
        operation_id=OPERATION_ID,
        wallet_payload=wallet_payload,
        payment_type='card',
        complement_payment=complement_payment,
    )
    customer_services_mock = mock_order_revision_customer_services(
        customer_services=customer_services,
    )
    customer_services_details_mock = (
        mock_order_revision_customer_services_details(
            customer_services=customer_services,
        )
    )
    mock_order_revision_list()

    await check_refund()

    assert customer_services_mock.times_called == 1
    assert customer_services_details_mock.times_called == 1
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1

    fetch_operation('test_order', 'abcd', prev_revision='bbbb')


@pytest.mark.parametrize(
    'cleared_items, response_status',
    [
        (
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac',
                            amount='2.00',
                            fiscal_receipt_info={
                                'personal_tin_id': 'personal-tin-id',
                                'title': 'Big Mac Burger',
                                'vat': 'nds_20',
                            },
                        ),
                    ],
                ),
            ],
            200,
        ),
        ([], 409),
    ],
)
async def test_refund_cleared_items(
        check_refund,
        mock_refund_invoice_retrieve,
        mockserver,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        pgsql,
        cleared_items,
        response_status,
):
    order = db_order.DBOrder(pgsql=pgsql, order_id=ORDER_ID, api_version=2)
    order.upsert()

    items = [
        helpers.make_transactions_item(
            item_id='composition-products-0', amount='2.00',
        ),
        helpers.make_transactions_item(item_id='delivery-0', amount='3.00'),
        helpers.make_transactions_item(item_id='assembly-0', amount='3.00'),
    ]
    previous_operation_items = [
        helpers.make_transactions_payment_items(
            payment_type='card', items=items,
        ),
    ]
    operation1 = helpers.make_operation(
        created='2021-03-06T12:00:00.000000+03:00',
        sum_to_pay=previous_operation_items,
    )

    invoice_retrieve_mock = mock_refund_invoice_retrieve(
        items=cleared_items,
        invoice_status='cleared',
        operations=[operation1],
        cleared=cleared_items,
    )

    # pylint: disable=unused-variable,invalid-name
    @mockserver.json_handler('/transactions-eda/v2/invoice/update')
    def transactions_update_invoice_handler(request):
        return {}

    mock_order_revision_customer_services(customer_services=[])
    mock_order_revision_customer_services_details(customer_services=[])
    await check_refund(response_status=response_status)

    assert invoice_retrieve_mock.times_called == 1


@pytest.mark.parametrize('is_need_new_revision_service', [True, False])
async def test_total_amount_greater_than_previous(
        check_refund,
        pgsql,
        mock_refund_invoice_retrieve,
        mockserver,
        experiments3,
        is_need_new_revision_service,
):
    experiments3.add_experiment(
        **helpers.make_new_service_revision(is_need_new_revision_service),
    )
    order = db_order.DBOrder(pgsql=pgsql, order_id=ORDER_ID, api_version=2)
    order.upsert()

    previous_operation_items = [
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='composition-products-0', amount='2.00',
                ),
                helpers.make_transactions_item(
                    item_id='delivery-0', amount='3.00',
                ),
                helpers.make_transactions_item(
                    item_id='assembly-0', amount='3.00',
                ),
            ],
        ),
    ]
    operation1 = helpers.make_operation(
        created='2021-03-06T12:00:00.000000+03:00',
        sum_to_pay=previous_operation_items,
    )
    invoice_retrieve_mock = mock_refund_invoice_retrieve(
        items=[], operations=[operation1],
    )

    customer_services_1 = [
        helpers.make_customer_service(
            customer_service_id='composition-products-0',
            name='Composition products',
            cost_for_customer='10.00',
            currency='RUB',
            customer_service_type='composition_products',
            vat='nds_18',
            trust_product_id='burger',
            place_id='place_1',
        ),
        helpers.make_customer_service(
            customer_service_id='delivery-0',
            name='Delivery',
            cost_for_customer='12.00',
            currency='RUB',
            customer_service_type='delivery',
            vat='nds_18',
            trust_product_id='burger',
            place_id='place_1',
        ),
    ]
    customer_services_2 = [
        helpers.make_customer_service(
            customer_service_id='composition-products-0',
            name='Composition products',
            cost_for_customer='5.00',
            currency='RUB',
            customer_service_type='composition_products',
            vat='nds_18',
            trust_product_id='burger',
            place_id='place_1',
        ),
        helpers.make_customer_service(
            customer_service_id='delivery-0',
            name='Delivery',
            cost_for_customer='6.00',
            currency='RUB',
            customer_service_type='delivery',
            vat='nds_18',
            trust_product_id='burger',
            place_id='place_1',
        ),
    ]

    # pylint: disable=unused-variable,invalid-name
    @mockserver.json_handler(
        '/eats-core-order-revision/internal-api/'
        'v1/order-revision/customer-services',
    )
    @mockserver.json_handler(
        '/eats-order-revision/' 'v1/order-revision/customer-services',
    )
    def mock_order_revision_customer_services(request):
        if (
                (
                    'revision_id' in request.json
                    and request.json['revision_id'] == '12345'
                )
                or (
                    'origin_revision_id' in request.json
                    and request.json['origin_revision_id'] == '12345'
                )
        ):
            return mockserver.make_response(
                status=200,
                json={
                    'customer_services': customer_services_2,
                    'revision_id': '123-321',
                    'origin_revision_id': '123-321',
                    'created_at': '2020-03-30T08:29:06+00:00',
                },
            )
        if (
                (
                    'revision_id' in request.json
                    and request.json['revision_id'] == 'abcd'
                )
                or (
                    'origin_revision_id' in request.json
                    and request.json['origin_revision_id'] == 'abcd'
                )
        ):
            return mockserver.make_response(
                status=200,
                json={
                    'customer_services': customer_services_1,
                    'revision_id': '123-321',
                    'origin_revision_id': '123-321',
                    'created_at': '2020-03-30T08:29:06+00:00',
                },
            )
        return {}

    # pylint: disable=unused-variable,invalid-name
    @mockserver.json_handler(
        '/eats-order-revision/' 'v1/order-revision/customer-services/details',
    )
    @mockserver.json_handler(
        '/eats-core-order-revision/internal-api/'
        'v1/order-revision/customer-services/details',
    )
    def mock_order_revision_customer_services_details(request):
        if (
                (
                    'revision_id' in request.json
                    and request.json['revision_id'] == '12345'
                )
                or (
                    'origin_revision_id' in request.json
                    and request.json['origin_revision_id'] == '12345'
                )
        ):
            return mockserver.make_response(
                status=200,
                json={
                    'customer_services': customer_services_2,
                    'revision_id': '123-321',
                    'origin_revision_id': '123-321',
                    'created_at': '2020-03-30T08:29:06+00:00',
                },
            )
        if (
                (
                    'revision_id' in request.json
                    and request.json['revision_id'] == 'abcd'
                )
                or (
                    'origin_revision_id' in request.json
                    and request.json['origin_revision_id'] == 'abcd'
                )
        ):
            return mockserver.make_response(
                status=200,
                json={
                    'customer_services': customer_services_1,
                    'revision_id': '123-321',
                    'origin_revision_id': '123-321',
                    'created_at': '2020-03-30T08:29:06+00:00',
                },
            )
        return {}

    await check_refund(response_status=400)

    assert invoice_retrieve_mock.times_called == 1


async def test_api_version_mismatch(check_refund, pgsql):
    order = db_order.DBOrder(pgsql=pgsql, order_id=ORDER_ID, api_version=1)
    order.upsert()

    await check_refund(response_status=400)


@pytest.mark.config(
    EATS_PAYMENTS_FEATURE_FLAGS={
        'sbp_skip_invoice_update_on_refund': {
            'description': '',
            'enabled': True,
        },
    },
)
@pytest.mark.parametrize(
    'cleared_items, response_status',
    [
        pytest.param(
            # cleared_items
            [
                helpers.make_transactions_payment_items(
                    payment_type='sbp',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac',
                            amount='0.99',
                            fiscal_receipt_info={
                                'personal_tin_id': 'personal-tin-id',
                                'title': 'Big Mac Burger',
                                'vat': 'nds_20',
                            },
                        ),
                    ],
                ),
            ],
            200,
            id='Skip invoice update',
        ),
    ],
)
async def test_refund_sbp(
        check_refund,
        mock_refund_invoice_retrieve,
        mockserver,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        pgsql,
        cleared_items,
        response_status,
):
    order = db_order.DBOrder(pgsql=pgsql, order_id=ORDER_ID, api_version=2)
    order.upsert()

    items = [
        helpers.make_transactions_item(
            item_id='composition-products-0', amount='0.99',
        ),
        helpers.make_transactions_item(item_id='delivery-0', amount='3.00'),
        helpers.make_transactions_item(item_id='assembly-0', amount='3.00'),
    ]
    previous_operation_items = [
        helpers.make_transactions_payment_items(
            payment_type='sbp', items=items,
        ),
    ]
    operation1 = helpers.make_operation(
        created='2021-03-06T12:00:00.000000+03:00',
        sum_to_pay=previous_operation_items,
    )

    invoice_retrieve_mock = mock_refund_invoice_retrieve(
        items=cleared_items,
        invoice_status='cleared',
        operations=[operation1],
        cleared=cleared_items,
        file_to_load='retrieve_invoice_sbp.json',
    )

    mock_order_revision_customer_services(customer_services=[])
    mock_order_revision_customer_services_details(customer_services=[])
    await check_refund(response_status=response_status)

    assert invoice_retrieve_mock.times_called == 1


async def test_refund_cash(
        check_refund, pgsql, upsert_order, upsert_order_payment,
):
    order = db_order.DBOrder(pgsql=pgsql, order_id=ORDER_ID, api_version=2)
    order.upsert()

    upsert_order(ORDER_ID, cancelled=True)
    upsert_order_payment(
        order_id=ORDER_ID,
        payment_id=consts.CASH_PAYMENT_TYPE,
        payment_type=consts.CASH_PAYMENT_TYPE,
    )

    await check_refund(response_status=400)
