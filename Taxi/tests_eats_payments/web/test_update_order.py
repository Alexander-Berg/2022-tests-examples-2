import typing

import pytest


from tests_eats_payments import consts
from tests_eats_payments import helpers

URL = 'v1/orders/update'


@pytest.fixture(name='check_update_order')
def check_update_order_fixture(
        upsert_order, taxi_eats_payments, mockserver, load_json,
):
    upsert_order('test_order')

    async def _inner(
            items: typing.Optional[typing.List[dict]] = None,
            payment_type: typing.Optional[str] = 'card',
            payment_method_id: typing.Optional[str] = '123',
            response_status=200,
            response_body=None,
            ttl: int = None,
    ):
        request_payload = {
            'id': 'test_order',
            'version': 2,
            'revision': 'abcd',
        }
        if payment_type is not None:
            request_payload['payment_method'] = {
                'id': payment_method_id,
                'type': payment_type,
            }

        payload: typing.Dict[str, typing.Any] = {
            **request_payload,
            'items': items or [],
        }
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
async def test_basic(
        check_update_order,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        payment_type,
):
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                payment_type=payment_type, operation_id='create:100500',
            ),
        ],
        items=[],
        payment_types=[payment_type],
    )
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    transactions_items = helpers.make_transactions_payment_items(
        payment_type=payment_type,
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], payment_type=payment_type,
    )
    await check_update_order(items=items, payment_type=payment_type)
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1


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
        check_update_order,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        transactions,
):
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        items=[], transactions=transactions,
    )
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    invoice_update_mock = mock_transactions_invoice_update(
        items=[], payment_type=None,
    )
    await check_update_order(
        items=items,
        response_status=500,
        payment_type=None,
        payment_method_id=None,
    )
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 0


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
        check_update_order,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        transactions,
):
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

    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    await check_update_order(
        items=items,
        payment_type='card',
        payment_method_id='some-card-payment-id',
    )

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1


async def test_items_info_updated(
        check_update_order,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        insert_items,
        fetch_items_from_db,
):
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='123',
                balance_client_id='456',
                item_type='baz',
            ),
            helpers.make_db_row(
                item_id='cola',
                place_id='123',
                balance_client_id='456',
                item_type='baz',
            ),
        ],
    )
    mock_transactions_invoice_retrieve(items=[])
    items = [
        helpers.make_item(
            item_id='big_mac',
            amount='2.00',
            billing_info={
                'place_id': 'some_place_id',
                'balance_client_id': 'some_id',
                'item_type': 'product',
            },
        ),
        helpers.make_item(
            item_id='cheeseburger',
            amount='3.00',
            billing_info={
                'place_id': 'some_place_id',
                'balance_client_id': 'some_id',
                'item_type': 'product',
            },
        ),
    ]
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
            helpers.make_transactions_item(
                item_id='cheeseburger', amount='3.00',
            ),
        ],
    )
    mock_transactions_invoice_update(
        items=[transactions_items], payment_type='card',
    )
    await check_update_order(items=items)

    db_items = fetch_items_from_db('test_order')
    assert db_items == [
        helpers.make_db_row(
            item_id='cola',
            place_id='123',
            balance_client_id='456',
            item_type='baz',
        ),
        helpers.make_db_row(
            item_id='big_mac',
            place_id='some_place_id',
            balance_client_id='some_id',
            item_type='product',
        ),
        helpers.make_db_row(
            item_id='cheeseburger',
            place_id='some_place_id',
            balance_client_id='some_id',
            item_type='product',
        ),
    ]


async def test_fiscal_info_passed(
        check_update_order,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        fetch_items_from_db,
):
    mock_transactions_invoice_retrieve(items=[])
    items = [
        helpers.make_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': '634333f24bc54736b4ad70dcf69759c7',
                'vat': 'nds_20',
                'title': 'Big Mac Burger',
            },
        ),
        helpers.make_item(
            item_id='long_title',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': '634333f24bc54736b4ad70dcf69759c7',
                'vat': 'nds_20',
                'title': consts.LONG_ITEM_TITLE,
            },
        ),
        helpers.make_item(
            item_id='not_long_title',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': '634333f24bc54736b4ad70dcf69759c7',
                'vat': 'nds_20',
                'title': consts.NOT_LONG_ITEM_TITLE,
            },
        ),
    ]
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
                    'title': consts.LONG_ITEM_TITLE_TRIMMED,
                },
            ),
            helpers.make_transactions_item(
                item_id='not_long_title',
                amount='2.00',
                fiscal_receipt_info={
                    'personal_tin_id': '634333f24bc54736b4ad70dcf69759c7',
                    'vat': 'nds_20',
                    'title': consts.NOT_LONG_ITEM_TITLE,
                },
            ),
        ],
    )
    mock_transactions_invoice_update(
        items=[transactions_items], payment_type='card',
    )
    await check_update_order(items=items)

    db_items = fetch_items_from_db('test_order')
    assert db_items == []


async def test_no_billing_and_fiscal_info_ok(
        check_update_order,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        fetch_items_from_db,
):
    mock_transactions_invoice_retrieve(items=[])
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    mock_transactions_invoice_update(
        items=[transactions_items], payment_type='card',
    )
    await check_update_order(items=items)

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
        check_update_order,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mockserver,
        invoice_update_response,
        response_status,
        response_body,
):
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(items=[])
    invoice_update_mock = mock_transactions_invoice_update(
        invoice_update_response=invoice_update_response,
    )
    await check_update_order(
        response_status=response_status, response_body=response_body,
    )
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1


@pytest.mark.parametrize('payment_type', consts.CLIENT_PAYMENT_TYPES)
async def test_passing_ttl_to_transactions(
        check_update_order,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        payment_type,
):
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                payment_type=payment_type, operation_id='create:100500',
            ),
        ],
        items=[],
        payment_types=[payment_type],
    )
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    transactions_items = helpers.make_transactions_payment_items(
        payment_type=payment_type,
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items], payment_type=payment_type, ttl=600,
    )
    await check_update_order(items=items, ttl=10, payment_type=payment_type)
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1


@pytest.mark.parametrize(
    'pass_afs_params, trust_afs_params',
    [
        (False, None),  # pass_afs_params  # trust_afs_params
        (True, {'request': 'mit'}),  # pass_afs_params  # trust_afs_params
    ],
)
async def test_afs_payloades_passed_update(
        check_update_order,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        experiments3,
        pass_afs_params,
        trust_afs_params,
):
    payment_type = 'card'
    experiments3.add_config(
        **helpers.make_pass_afs_params_experiment(pass_afs_params),
    )

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                payment_type=payment_type, operation_id='create:100500',
            ),
        ],
        items=[],
        payment_types=[payment_type],
    )
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    transactions_items = helpers.make_transactions_payment_items(
        payment_type=payment_type,
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items],
        payment_type=payment_type,
        ttl=600,
        trust_afs_params=trust_afs_params,
    )
    await check_update_order(items=items, ttl=10, payment_type=payment_type)
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
