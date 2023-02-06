import pytest

from tests_eats_billing_processor.fines import helper


@pytest.mark.pgsql('eats_billing_processor', files=['order_fines.sql'])
async def test_order_fine(fines_fixtures):
    await (
        helper.OrderFinesTest()
        .on_request(order_nr='123456')
        .expect_order_fine(
            fine_id='1',
            amount='12.33',
            currency='RUB',
            is_appealed=False,
            fine_reason='refund',
            fine_reason_id='1',
        )
        .run(fines_fixtures)
    )


@pytest.mark.pgsql('eats_billing_processor', files=['order_fines.sql'])
async def test_many_order_fines(fines_fixtures):
    await (
        helper.OrderFinesTest()
        .on_request(order_nr='12345')
        .expect_order_fine(
            fine_id='2',
            amount='12.33',
            currency='RUB',
            is_appealed=True,
            ticket='test',
            fine_reason='refund',
            fine_reason_id='2',
        )
        .expect_order_fine(
            fine_id='3',
            amount='12.33',
            currency='RUB',
            is_appealed=False,
            fine_reason='cancel',
            fine_reason_id='1',
        )
        .run(fines_fixtures)
    )


async def test_empty_response(fines_fixtures):
    await (
        helper.OrderFinesTest().on_request(order_nr='1').run(fines_fixtures)
    )
