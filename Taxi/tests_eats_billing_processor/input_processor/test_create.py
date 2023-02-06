import pytest

from tests_eats_billing_processor.input_processor import helper


@pytest.mark.parametrize(
    'kind, rule_name',
    [
        pytest.param('monthly_payment', 'default'),
        pytest.param('additional_promo_payment', 'shop'),
        pytest.param('mercury_discount', 'inplace'),
        pytest.param('billing_payment', 'default'),
        pytest.param('billing_refund', 'default'),
        pytest.param('billing_commission', 'default'),
        pytest.param('receipt', 'retail'),
        pytest.param('order_gmv', 'default'),
        pytest.param('payment_received', 'restaurant'),
        pytest.param('payment_refund', 'retail'),
        pytest.param('payment_not_received', 'pickup'),
        pytest.param('order_cancelled', 'marketplace'),
        pytest.param('order_delivered', 'shop'),
        pytest.param('compensation', 'restaurant'),
        pytest.param('plus_cashback_emission', 'default'),
        pytest.param('payment_update_plus_cashback', 'shop_marketplace'),
        pytest.param('fine_appeal', 'default'),
        pytest.param('courier_earning', 'default'),
    ],
)
async def test_create_happy_path(input_processor_fixtures, kind, rule_name):
    await (
        helper.InputProcessorTest()
        .request(
            order_nr='123456',
            external_id='event/123456',
            event_at='2021-03-18T15:00:00+00:00',
            kind=kind,
            rule_name=rule_name,
            data=input_processor_fixtures.load_json(f'v1/{kind}.json'),
        )
        .expected_rule_name(rule_name)
        .run(input_processor_fixtures)
    )


@pytest.mark.parametrize(
    'kind',
    [
        pytest.param('payment_accounting_correction'),
        pytest.param('commission_accounting_correction'),
        pytest.param('all_accounting_correction'),
    ],
)
async def test_create_happy_path_correction(input_processor_fixtures, kind):
    await (
        helper.InputProcessorTest()
        .request(
            order_nr='123456',
            external_id='event/123456',
            event_at='2021-03-18T15:00:00+00:00',
            kind=kind,
            data=input_processor_fixtures.load_json(f'v1/{kind}.json'),
        )
        .expected_rule_name('default')
        .expected_result_append({'payload': {'correction_id': '12345'}})
        .run(input_processor_fixtures)
    )


@pytest.mark.parametrize(
    'kind',
    [
        pytest.param('payment_received'),
        pytest.param('payment_refund'),
        pytest.param('plus_cashback_emission'),
        pytest.param('payment_update_plus_cashback'),
    ],
)
@pytest.mark.config(
    EATS_BILLING_PROCESSOR_FEATURES={
        'create_handler_enabled': True,
        'grocery_rules_enabled': True,
    },
)
async def test_grocery_eats_flow(input_processor_fixtures, kind):
    await (
        helper.InputProcessorTest()
        .request(
            order_nr='123456-grocery',
            external_id='event/123456',
            event_at='2021-03-18T15:00:00+00:00',
            kind=kind,
            data=input_processor_fixtures.load_json(f'v1/{kind}.json'),
        )
        .expected_rule_name('grocery_eats_flow')
        .run(input_processor_fixtures)
    )


@pytest.mark.parametrize(
    'kind', [pytest.param('payment_received'), pytest.param('payment_refund')],
)
@pytest.mark.config(
    EATS_BILLING_PROCESSOR_FEATURES={
        'create_handler_enabled': True,
        'grocery_rules_enabled': True,
    },
)
async def test_grocery(input_processor_fixtures, kind):
    data = input_processor_fixtures.load_json(f'v1/{kind}.json')
    data['client_id'] = helper.GROCERY_CLIENT_ID
    await (
        helper.InputProcessorTest()
        .request(
            order_nr='123456',
            external_id='event/123456',
            event_at='2021-03-18T15:00:00+00:00',
            kind=kind,
            data=data,
        )
        .expected_rule_name('grocery')
        .run(input_processor_fixtures)
    )


@pytest.mark.parametrize(
    'kind', [pytest.param('payment_received'), pytest.param('payment_refund')],
)
async def test_donation(input_processor_fixtures, kind):
    data = input_processor_fixtures.load_json(f'v1/{kind}.json')
    data['product_type'] = 'donation'
    await (
        helper.InputProcessorTest()
        .request(
            order_nr='123456',
            external_id='event/123456',
            event_at='2021-03-18T15:00:00+00:00',
            kind=kind,
            data=data,
        )
        .expected_rule_name('donation')
        .run(input_processor_fixtures)
    )


async def test_create_incorrect_client_id(input_processor_fixtures):
    data = input_processor_fixtures.load_json('v1/payment_refund.json')
    data['client_id'] = 'sadasd'
    await (
        helper.InputProcessorTest()
        .request(
            order_nr='123456',
            external_id='payment/123456',
            event_at='2021-03-18T15:00:00+00:00',
            kind='payment_refund',
            data=data,
        )
        .should_fail(
            status=400,
            code='400',
            message=f'Parse error at pos 493, path \'data\': '
            f'Value of \'/\' cannot be parsed as a variant',
        )
        .run(input_processor_fixtures)
    )


async def test_create_incorrect_client_id_2(input_processor_fixtures):
    data = input_processor_fixtures.load_json('v1/payment_refund.json')
    data['client_id'] = '0213'
    await (
        helper.InputProcessorTest()
        .request(
            order_nr='123456',
            external_id='payment/123456',
            event_at='2021-03-18T15:00:00+00:00',
            kind='payment_refund',
            data=data,
        )
        .should_fail(
            status=400,
            code='400',
            message=f'Parse error at pos 491, path \'data\': '
            f'Value of \'/\' cannot be parsed as a variant',
        )
        .run(input_processor_fixtures)
    )


async def test_create_new_order(input_processor_fixtures):
    await (
        helper.InputProcessorTest()
        .request(
            order_nr='123456',
            external_id='create/123456',
            event_at='2021-03-18T15:00:00+00:00',
            kind='order_created',
            data={'rules': 'retail'},
            rule_name='retail',
        )
        .no_stq_call()
        .run(input_processor_fixtures)
    )


async def test_create_idempotency(input_processor_fixtures):
    await (
        helper.InputProcessorTest()
        .request(
            order_nr='210318-000001',
            external_id='existing_event',
            event_at='2021-03-18T15:34:00+00:00',
            kind='order_created',
            data={'rules': 'restaurant'},
            rule_name='restaurant',
        )
        .expected_response(event_id='1')
        .no_stq_call()
        .run(input_processor_fixtures)
    )


async def test_create_unknown_kind(input_processor_fixtures):
    await (
        helper.InputProcessorTest()
        .request(
            order_nr='210319-000001',
            external_id='incorrect_event',
            event_at='2021-03-18T15:34:00+00:00',
            kind='billing_payment',
            data={'rules': 'my_rules'},
        )
        .should_fail(
            status=400,
            code='INCORRECT_DATA',
            message='Data format doesn\'t match'
            ' event kind \'billing_payment\'',
        )
        .run(input_processor_fixtures)
    )


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_FEATURES={'create_handler_enabled': False},
)
async def test_feature_flag(input_processor_fixtures):
    await (
        helper.InputProcessorTest()
        .request(
            order_nr='123456',
            external_id='payment/123456',
            event_at='2021-03-18T15:00:00+00:00',
            kind='billing_payment',
            data=input_processor_fixtures.load_json('v1/billing_payment.json'),
        )
        .expected_response(event_id='')
        .no_database_insertion()
        .no_stq_call()
        .run(input_processor_fixtures)
    )


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_FEATURES={
        'create_handler_enabled': True,
        'create_handler_whitelist': ('order_canceled',),
    },
)
async def test_not_find_create_handler_whitelist(input_processor_fixtures):
    await (
        helper.InputProcessorTest()
        .request(
            order_nr='123456',
            external_id='payment/123456',
            event_at='2021-03-18T15:00:00+00:00',
            kind='billing_payment',
            data=input_processor_fixtures.load_json('v1/billing_payment.json'),
        )
        .expected_response(event_id='')
        .no_database_insertion()
        .no_stq_call()
        .run(input_processor_fixtures)
    )


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_FEATURES={
        'create_handler_enabled': True,
        'create_handler_whitelist': ('billing_payment',),
    },
)
async def test_find_create_handler_whitelist(input_processor_fixtures):
    await (
        helper.InputProcessorTest()
        .request(
            order_nr='123456',
            external_id='payment/123456',
            event_at='2021-03-18T15:00:00+00:00',
            kind='billing_payment',
            data=input_processor_fixtures.load_json('v1/billing_payment.json'),
        )
        .expected_response(event_id='1')
        .run(input_processor_fixtures)
    )
