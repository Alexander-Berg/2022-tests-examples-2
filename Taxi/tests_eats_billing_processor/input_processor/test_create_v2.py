import pytest

from tests_eats_billing_processor.input_processor import helper


@pytest.mark.parametrize(
    'kind',
    [
        pytest.param('payment_update_plus_cashback'),
        pytest.param('payment_not_received'),
        pytest.param('plus_cashback_emission'),
        pytest.param('order_cancelled'),
        pytest.param('order_delivered'),
        pytest.param('order_gmv'),
        pytest.param('receipt'),
        pytest.param('compensation'),
        pytest.param('payment_received'),
        pytest.param('payment_refund'),
        pytest.param('monthly_payment'),
        pytest.param('mercury_discount'),
        pytest.param('additional_promo_payment'),
        pytest.param('fine_appeal'),
    ],
)
async def test_create_happy_path(input_processor_fixtures, kind):
    await (
        helper.InputProcessorTestV2()
        .request(
            order_nr='123456',
            external_id='event/123456',
            event_at='2022-01-27T12:00:00+00:00',
            data=input_processor_fixtures.load_json(f'v2/{kind}.json'),
        )
        .run(input_processor_fixtures)
    )


async def test_create_incorrect_format(input_processor_fixtures):
    await (
        helper.InputProcessorTestV2()
        .request(
            order_nr='123456',
            external_id='event/123456',
            event_at='2022-01-27T12:00:00+00:00',
            data={'incorrect': 'data'},
        )
        .should_fail(status=400)
        .run(input_processor_fixtures)
    )
