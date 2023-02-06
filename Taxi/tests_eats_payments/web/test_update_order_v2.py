# pylint: disable=too-many-lines
import typing

import pytest


from tests_eats_payments import consts
from tests_eats_payments import db_order
from tests_eats_payments import helpers

URL = 'v2/orders/update'


@pytest.fixture(name='check_update_order_v2')
def check_update_order_fixture(taxi_eats_payments, mockserver, load_json):
    async def _inner(
            order_id='test_order',
            payment_type: typing.Optional[str] = 'card',
            payment_method_id: typing.Optional[str] = '123',
            response_status=200,
            response_body=None,
            revision='abcd',
            ttl: int = None,
    ):
        request_payload = {'id': order_id, 'version': 2, 'revision': revision}
        if payment_type is not None:
            request_payload['payment_method'] = {
                'id': payment_method_id,
                'type': payment_type,
            }

        payload: typing.Dict[str, typing.Any] = {**request_payload}
        if ttl is not None:
            payload['ttl'] = ttl
        response = await taxi_eats_payments.post(
            URL, json=payload, headers=consts.BASE_HEADERS,
        )
        assert response.status == response_status
        if response_body is not None:
            assert response.json() == response_body

    return _inner


@pytest.mark.parametrize('payment_type', consts.CLIENT_PAYMENT_TYPES)
@pytest.mark.parametrize('is_need_new_revision_service', [True, False])
async def test_basic(
        check_update_order_v2,
        pgsql,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_list,
        payment_type,
        is_need_new_revision_service,
        experiments3,
):
    experiments3.add_experiment(
        **helpers.make_new_service_revision(is_need_new_revision_service),
    )
    order = db_order.DBOrder(pgsql=pgsql, order_id='test_order', api_version=2)
    order.upsert()

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                payment_type=payment_type, operation_id='create:100500',
            ),
        ],
        payment_types=[payment_type],
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type=payment_type,
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    customer_services = [
        helpers.make_customer_service(
            customer_service_id='big_mac',
            name='big_mac',
            cost_for_customer='2.00',
            currency='RUB',
            customer_service_type='retail',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
        ),
    ]
    customer_services_details_mock = (
        mock_order_revision_customer_services_details(
            customer_services=customer_services,
        )
    )
    list_mock = mock_order_revision_list()
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], payment_type=payment_type,
    )
    await check_update_order_v2(payment_type=payment_type)
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert customer_services_details_mock.times_called == 1
    assert list_mock.times_called == 1


@pytest.mark.config(
    EATS_PAYMENTS_FEATURE_FLAGS={
        'find_prev_revision_in_operations': {
            'description': '',
            'enabled': False,
        },
    },
)
@pytest.mark.parametrize('payment_type', ['card'])
async def test_basic_operation(
        check_update_order_v2,
        pgsql,
        experiments3,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_list,
        payment_type,
        fetch_operation,
):
    experiments3.add_config(**helpers.make_operations_config())

    order = db_order.DBOrder(pgsql=pgsql, order_id='test_order', api_version=2)
    order.upsert()

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                payment_type=payment_type, operation_id='create:100500',
            ),
        ],
        payment_types=[payment_type],
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type=payment_type,
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    customer_services = [
        helpers.make_customer_service(
            customer_service_id='big_mac',
            name='big_mac',
            cost_for_customer='2.00',
            currency='RUB',
            customer_service_type='retail',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
        ),
    ]
    customer_services_details_mock = (
        mock_order_revision_customer_services_details(
            customer_services=customer_services,
        )
    )
    list_mock = mock_order_revision_list()
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], payment_type=payment_type,
    )

    await check_update_order_v2(payment_type=payment_type)
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert customer_services_details_mock.times_called == 1
    assert list_mock.times_called == 1

    fetch_operation('test_order', 'abcd', prev_revision='bbbb')


async def test_update_cash(
        upsert_order,
        upsert_order_payment,
        insert_operation,
        check_update_order_v2,
        experiments3,
        fetch_operation,
        stq,
):
    order_id = 'test_order'
    payment_type = consts.CASH_PAYMENT_TYPE
    payment_method_id = 'cash_test_id'
    previous_revision = 'ab'
    revision = 'cd'

    experiments3.add_config(**helpers.make_operations_config())

    upsert_order(order_id=order_id, api_version=2)
    upsert_order_payment(
        order_id=order_id,
        payment_id=payment_method_id,
        payment_type=payment_type,
    )
    insert_operation(
        order_id=order_id,
        revision=previous_revision,
        prev_revision=previous_revision,
        op_type='create',
        status='done',
        fails_count=0,
    )

    await check_update_order_v2(
        order_id=order_id,
        revision=revision,
        payment_type=payment_type,
        payment_method_id=payment_method_id,
    )

    fetch_operation(order_id, revision, prev_revision=previous_revision)

    helpers.check_callback_mock(
        callback_mock=stq.eda_order_processing_payment_events_callback,
        times_called=1,
        task_id='test_order:update:cd:done:operation_finish',
        queue='eda_order_processing_payment_events_callback',
        **{
            'order_id': order_id,
            'action': 'update',
            'status': 'confirmed',
            'revision': revision,
        },
    )


@pytest.mark.config(
    EATS_PAYMENTS_FEATURE_FLAGS={
        'find_prev_revision_in_operations': {
            'description': '',
            'enabled': True,
        },
    },
)
@pytest.mark.parametrize('payment_type', ['card'])
async def test_basic_operation_find_prev_revision_in_operations(
        check_update_order_v2,
        pgsql,
        experiments3,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_list,
        payment_type,
        insert_operation,
        fetch_operation,
):
    experiments3.add_config(**helpers.make_operations_config())

    order = db_order.DBOrder(pgsql=pgsql, order_id='test_order', api_version=2)
    order.upsert()

    insert_operation('test_order', 'bbbb', 'bbbb', 'create', 'in_progress', 1)

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                payment_type=payment_type, operation_id='create:100500',
            ),
        ],
        payment_types=[payment_type],
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type=payment_type,
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    customer_services = [
        helpers.make_customer_service(
            customer_service_id='big_mac',
            name='big_mac',
            cost_for_customer='2.00',
            currency='RUB',
            customer_service_type='retail',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
        ),
    ]
    customer_services_details_mock = (
        mock_order_revision_customer_services_details(
            customer_services=customer_services,
        )
    )
    list_mock = mock_order_revision_list()
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], payment_type=payment_type,
    )

    await check_update_order_v2(payment_type=payment_type)
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert customer_services_details_mock.times_called == 1
    assert list_mock.times_called == 1

    fetch_operation('test_order', 'abcd', prev_revision='bbbb')


@pytest.mark.parametrize(
    'transactions',
    (
        pytest.param([], id='No transactions'),
        pytest.param(
            [helpers.make_transaction(payment_type=None)],
            id='Transaction with no `payment_type`',
        ),
        pytest.param(
            [helpers.make_transaction(payment_method_id=None)],
            id='Transaction with no `payment_method_id`',
        ),
    ),
)
async def test_unable_to_determine_payment_method_error(
        check_update_order_v2,
        pgsql,
        mock_order_revision_customer_services,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        transactions,
):
    order = db_order.DBOrder(pgsql=pgsql, order_id='test_order', api_version=2)
    order.upsert()

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        items=[], transactions=transactions,
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[], payment_type=None,
    )
    customer_services = [
        helpers.make_customer_service(
            customer_service_id='big_mac',
            name='big_mac',
            cost_for_customer='2.00',
            currency='RUB',
            customer_service_type='retail',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
        ),
    ]
    customer_services_mock = mock_order_revision_customer_services(
        customer_services=customer_services,
    )
    await check_update_order_v2(
        response_status=500, payment_type=None, payment_method_id=None,
    )
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 0
    assert customer_services_mock.times_called == 0


@pytest.mark.parametrize(
    'transactions',
    (
        pytest.param(
            [
                helpers.make_transaction(
                    payment_type='card',
                    payment_method_id='some-card-payment-id',
                ),
                helpers.make_transaction(
                    payment_type='applepay',
                    payment_method_id='some-applepay-payment-id',
                ),
                helpers.make_transaction(
                    payment_type='googlepay',
                    payment_method_id='some-googlepay-payment-id',
                ),
            ],
            id='Multiple transactions.',
        ),
    ),
)
async def test_invoice_with_different_payments(
        check_update_order_v2,
        pgsql,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_list,
        transactions,
):
    order = db_order.DBOrder(pgsql=pgsql, order_id='test_order', api_version=2)
    order.upsert()

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        items=[], transactions=transactions,
    )

    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items],
        payment_type='card',
        payment_method_id='some-card-payment-id',
    )

    customer_services = [
        helpers.make_customer_service(
            customer_service_id='big_mac',
            name='big_mac',
            cost_for_customer='2.00',
            currency='RUB',
            customer_service_type='retail',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
        ),
    ]

    customer_services_details_mock = (
        mock_order_revision_customer_services_details(
            customer_services=customer_services,
        )
    )
    list_mock = mock_order_revision_list()

    await check_update_order_v2(
        payment_type='card', payment_method_id='some-card-payment-id',
    )

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert customer_services_details_mock.times_called == 1
    assert list_mock.times_called == 1


async def test_fiscal_info_passed(
        check_update_order_v2,
        pgsql,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_list,
        fetch_items_from_db,
):
    order = db_order.DBOrder(pgsql=pgsql, order_id='test_order', api_version=2)
    order.upsert()

    mock_transactions_invoice_retrieve(items=[])
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(
                item_id='big_mac',
                amount='2.00',
                fiscal_receipt_info={
                    'personal_tin_id': '634333f24bc54736b4ad70dcf69759c7',
                    'vat': 'nds_20',
                    'title': 'Big Mac Burger',
                },
            ),
            helpers.make_transactions_item(
                item_id='long_title',
                amount='2.00',
                fiscal_receipt_info={
                    'personal_tin_id': '634333f24bc54736b4ad70dcf69759c7',
                    'vat': 'nds_20',
                    'title': (
                        'Очень длинный текст, который специально написан так '
                        'и занимает немного больше, чем 128 символов, чтобы '
                        'посмотреть как оно обр...'
                    ),
                },
            ),
            helpers.make_transactions_item(
                item_id='not_long_title',
                amount='2.00',
                fiscal_receipt_info={
                    'personal_tin_id': '634333f24bc54736b4ad70dcf69759c7',
                    'vat': 'nds_20',
                    'title': (
                        'Не очень длинный текст, который специально написан '
                        'так, что занимает ровно 128 символов, чтобы '
                        'посмотреть, что оно не обрежется.'
                    ),
                },
            ),
        ],
    )
    mock_transactions_invoice_update(
        items=[transactions_items], payment_type='card',
    )
    customer_services = [
        helpers.make_customer_service(
            customer_service_id='big_mac',
            name='Big Mac Burger',
            cost_for_customer='2.00',
            currency='RUB',
            customer_service_type='retail',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
            personal_tin_id='634333f24bc54736b4ad70dcf69759c7',
        ),
        helpers.make_customer_service(
            customer_service_id='long_title',
            name=(
                'Очень длинный текст, который специально написан так '
                'и занимает немного больше, чем 128 символов, чтобы '
                'посмотреть как оно обр...'
            ),
            cost_for_customer='2.00',
            currency='RUB',
            customer_service_type='retail',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
            personal_tin_id='634333f24bc54736b4ad70dcf69759c7',
        ),
        helpers.make_customer_service(
            customer_service_id='not_long_title',
            name=(
                'Не очень длинный текст, который специально написан так, '
                'что занимает ровно 128 символов, чтобы посмотреть, что '
                'оно не обрежется.'
            ),
            cost_for_customer='2.00',
            currency='RUB',
            customer_service_type='retail',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
            personal_tin_id='634333f24bc54736b4ad70dcf69759c7',
        ),
    ]
    mock_order_revision_customer_services_details(
        customer_services=customer_services,
    )
    mock_order_revision_list()
    await check_update_order_v2()

    db_items = fetch_items_from_db('test_order')
    assert db_items == []


async def test_no_billing_and_fiscal_info_ok(
        check_update_order_v2,
        pgsql,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_list,
        fetch_items_from_db,
):
    order = db_order.DBOrder(pgsql=pgsql, order_id='test_order', api_version=2)
    order.upsert()

    mock_transactions_invoice_retrieve(items=[])
    customer_services = [
        helpers.make_customer_service(
            customer_service_id='big_mac',
            name='big_mac',
            cost_for_customer='2.00',
            currency='RUB',
            customer_service_type='retail',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
        ),
    ]
    mock_order_revision_customer_services(customer_services=customer_services)
    mock_order_revision_customer_services_details(
        customer_services=customer_services,
    )
    mock_order_revision_list()
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    mock_transactions_invoice_update(
        items=[transactions_items], payment_type='card',
    )
    await check_update_order_v2()

    db_items = fetch_items_from_db('test_order')
    assert db_items == []


@pytest.mark.parametrize(
    ('invoice_update_response,' 'response_status,' 'response_body'),
    [
        ({'status': 200, 'json': {}}, 200, {}),
        (
            {
                'status': 400,
                'json': {
                    'code': 'bad-request',
                    'message': 'something wrong was sent',
                },
            },
            400,
            {
                'code': 'bad-request',
                'message': (
                    'Transactions error while updating invoice. '
                    'Error: `something wrong was sent`'
                ),
            },
        ),
        (
            {'status': 404},
            404,
            {
                'code': 'invoice-not-found',
                'message': (
                    'Transactions error while updating invoice. '
                    'Error: `invoice not found`'
                ),
            },
        ),
        (
            {
                'status': 409,
                'json': {'code': 'conflict', 'message': 'conflict happened'},
            },
            409,
            {
                'code': 'conflict',
                'message': (
                    'Transactions error while updating invoice. '
                    'Error: `conflict happened`'
                ),
            },
        ),
        (
            {
                'status': 500,
                'json': {
                    'code': 'internal-server-error',
                    'message': 'exception',
                },
            },
            500,
            None,
        ),
    ],
)
async def test_update_invoice_errors(
        check_update_order_v2,
        pgsql,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_list,
        invoice_update_response,
        response_status,
        response_body,
):
    order = db_order.DBOrder(pgsql=pgsql, order_id='test_order', api_version=2)
    order.upsert()

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(items=[])
    invoice_update_mock = mock_transactions_invoice_update(
        invoice_update_response=invoice_update_response,
    )
    customer_services = []
    mock_order_revision_customer_services_details(
        customer_services=customer_services,
    )
    mock_order_revision_list()
    await check_update_order_v2(
        response_status=response_status, response_body=response_body,
    )
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1


@pytest.mark.parametrize('payment_type', consts.CLIENT_PAYMENT_TYPES)
async def test_passing_ttl_to_transactions(
        check_update_order_v2,
        pgsql,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_list,
        payment_type,
):
    order = db_order.DBOrder(pgsql=pgsql, order_id='test_order', api_version=2)
    order.upsert()

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                payment_type=payment_type, operation_id='create:100500',
            ),
        ],
        items=[],
        payment_types=[payment_type],
    )
    customer_services = [
        helpers.make_customer_service(
            customer_service_id='big_mac',
            name='big_mac',
            cost_for_customer='2.00',
            currency='RUB',
            customer_service_type='retail',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
        ),
    ]
    mock_order_revision_customer_services_details(
        customer_services=customer_services,
    )
    mock_order_revision_list()
    transactions_items = helpers.make_transactions_payment_items(
        payment_type=payment_type,
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], payment_type=payment_type, ttl=600,
    )
    await check_update_order_v2(ttl=10, payment_type=payment_type)
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1


@pytest.mark.parametrize('payment_type', consts.CLIENT_PAYMENT_TYPES)
async def test_revision_already_applied(
        check_update_order_v2,
        pgsql,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_list,
        payment_type,
):
    order = db_order.DBOrder(pgsql=pgsql, order_id='test_order', api_version=2)
    order.upsert()

    transactions_payment_items = (
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='big_mac_1',
                    amount='2.00',
                    fiscal_receipt_info={
                        'personal_tin_id': 'personal-tin-id',
                        'title': 'Big Mac Burger',
                        'vat': 'nds_20',
                    },
                ),
            ],
        ),
    )
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                payment_type=payment_type, operation_id='create:100500',
            ),
        ],
        payment_types=[payment_type],
        operations=[
            helpers.make_operation(
                id='create:aaaa', sum_to_pay=transactions_payment_items,
            ),
            helpers.make_operation(
                id='update:bbbb', sum_to_pay=transactions_payment_items,
            ),
        ],
    )
    customer_services_details_mock = (
        mock_order_revision_customer_services_details(customer_services=[])
    )
    list_mock = mock_order_revision_list(
        revisions=[
            {'revision_id': 'aaaa'},
            {'revision_id': 'abcd'},
            {'revision_id': 'bbbb'},
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update()

    await check_update_order_v2(payment_type=payment_type)
    assert invoice_retrieve_mock.times_called == 1
    assert list_mock.times_called == 1
    assert invoice_update_mock.times_called == 0
    assert customer_services_details_mock.times_called == 0


@pytest.mark.parametrize('payment_type', consts.CLIENT_PAYMENT_TYPES)
async def test_outdated_revision(
        check_update_order_v2,
        pgsql,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_list,
        payment_type,
):
    order = db_order.DBOrder(pgsql=pgsql, order_id='test_order', api_version=2)
    order.upsert()

    transactions_payment_items = (
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='big_mac_1',
                    amount='2.00',
                    fiscal_receipt_info={
                        'personal_tin_id': 'personal-tin-id',
                        'title': 'Big Mac Burger',
                        'vat': 'nds_20',
                    },
                ),
            ],
        ),
    )
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                payment_type=payment_type, operation_id='create:100500',
            ),
        ],
        payment_types=[payment_type],
        operations=[
            helpers.make_operation(
                id='create:aaaa', sum_to_pay=transactions_payment_items,
            ),
        ],
    )
    customer_services_details_mock = (
        mock_order_revision_customer_services_details(customer_services=[])
    )
    list_mock = mock_order_revision_list(
        revisions=[
            {'revision_id': 'aaaa'},
            {'revision_id': 'abcd'},
            {'revision_id': 'bbbb'},
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update()

    await check_update_order_v2(payment_type=payment_type, response_status=400)
    assert invoice_retrieve_mock.times_called == 1
    assert list_mock.times_called == 1
    assert invoice_update_mock.times_called == 0
    assert customer_services_details_mock.times_called == 0


async def test_api_version_mismatch(check_update_order_v2, pgsql):
    order = db_order.DBOrder(pgsql=pgsql, order_id='test_order', api_version=1)
    order.upsert()

    await check_update_order_v2(response_status=400)


@pytest.mark.parametrize('payment_type', consts.CLIENT_PAYMENT_TYPES)
async def test_apply_revision_not_in_list(
        check_update_order_v2,
        pgsql,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_list,
        payment_type,
):
    order = db_order.DBOrder(pgsql=pgsql, order_id='test_order', api_version=2)
    order.upsert()

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                payment_type=payment_type, operation_id='create:100500',
            ),
        ],
        payment_types=[payment_type],
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type=payment_type,
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    customer_services = [
        helpers.make_customer_service(
            customer_service_id='big_mac',
            name='big_mac',
            cost_for_customer='2.00',
            currency='RUB',
            customer_service_type='retail',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
        ),
    ]
    customer_services_details_mock = (
        mock_order_revision_customer_services_details(
            customer_services=customer_services,
        )
    )
    list_mock = mock_order_revision_list(
        revisions=[
            {'revision_id': 'R1'},
            {'revision_id': 'R2'},
            {'revision_id': 'R3'},
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], payment_type=payment_type,
    )
    await check_update_order_v2(payment_type=payment_type)
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert customer_services_details_mock.times_called == 1
    assert list_mock.times_called == 1


@pytest.mark.parametrize(
    'pass_afs_params, trust_afs_params',
    [
        (False, None),  # pass_afs_params  # trust_afs_params
        (True, {'request': 'mit'}),  # pass_afs_params  # trust_afs_params
    ],
)
async def test_afs_payloades_passed_update(
        check_update_order_v2,
        pgsql,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_list,
        experiments3,
        pass_afs_params,
        trust_afs_params,
):
    payment_type = 'card'
    experiments3.add_config(
        **helpers.make_pass_afs_params_experiment(pass_afs_params),
    )
    order = db_order.DBOrder(pgsql=pgsql, order_id='test_order', api_version=2)
    order.upsert()

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                payment_type=payment_type, operation_id='create:100500',
            ),
        ],
        payment_types=[payment_type],
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type=payment_type,
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    customer_services = [
        helpers.make_customer_service(
            customer_service_id='big_mac',
            name='big_mac',
            cost_for_customer='2.00',
            currency='RUB',
            customer_service_type='retail',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
        ),
    ]
    customer_services_details_mock = (
        mock_order_revision_customer_services_details(
            customer_services=customer_services,
        )
    )
    list_mock = mock_order_revision_list(
        revisions=[
            {'revision_id': 'R1'},
            {'revision_id': 'R2'},
            {'revision_id': 'R3'},
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items],
        payment_type=payment_type,
        trust_afs_params=trust_afs_params,
    )
    await check_update_order_v2(payment_type=payment_type)
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert customer_services_details_mock.times_called == 1
    assert list_mock.times_called == 1


@pytest.mark.parametrize(
    'payment_type', consts.CLIENT_PAYMENT_TYPES + ['cash'],
)
async def test_update_order_is_absent(check_update_order_v2, payment_type):
    await check_update_order_v2(payment_type=payment_type, response_status=404)


@pytest.mark.parametrize(
    'payment_type', consts.CLIENT_PAYMENT_TYPES + ['cash'],
)
async def test_update_order_is_cancelled(
        check_update_order_v2, upsert_order, payment_type,
):
    order_id = 'test_order'

    upsert_order(order_id, cancelled=True)

    await check_update_order_v2(
        order_id=order_id, payment_type=payment_type, response_status=400,
    )


@pytest.mark.config(
    EATS_PAYMENTS_FEATURE_FLAGS={
        'sbp_skip_invoice_update_on_update': {
            'description': '',
            'enabled': True,
        },
        'sbp_skip_invoice_update_on_up_changes': {
            'description': '',
            'enabled': True,
        },
    },
)
async def test_sbp_up_changes(
        check_update_order_v2,
        pgsql,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_order_revision_list,
):
    order = db_order.DBOrder(pgsql=pgsql, order_id='test_order', api_version=2)
    order.upsert()

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                payment_type='sbp',
                payment_method_id='123',
                operation_id='create:100500',
                payment_url='payment_url',
                trust_payment_id='trust_payment_id',
            ),
        ],
        payment_types=['sbp'],
    )
    customer_services = [
        helpers.make_customer_service(
            customer_service_id='big_mac',
            name='big_mac',
            cost_for_customer='10.00',
            currency='RUB',
            customer_service_type='retail',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
        ),
    ]
    list_mock = mock_order_revision_list()
    customer_services_details_mock = (
        mock_order_revision_customer_services_details(
            customer_services=customer_services,
        )
    )

    response_body = {
        'code': 'up-changes-are-not-allowed',
        'message': 'Up changes are not allowed for such payment method',
    }
    await check_update_order_v2(
        payment_type='sbp',
        payment_method_id='sbp_link',
        response_status=400,
        response_body=response_body,
    )
    assert invoice_retrieve_mock.times_called == 1
    assert customer_services_details_mock.times_called == 1
    assert list_mock.times_called == 1
