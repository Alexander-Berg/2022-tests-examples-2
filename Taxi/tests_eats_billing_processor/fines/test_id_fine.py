import pytest

from tests_eats_billing_processor.fines import helper


@pytest.mark.pgsql('eats_billing_processor', files=['order_fines.sql'])
async def test_id_fine(fines_fixtures):
    await (
        helper.OrderFinesTest()
        .on_request_by_id(fine_id='2')
        .expect_fine_by_id(
            fine_id='2',
            order_nr='12345',
            amount='12.33',
            currency='RUB',
            ticket='test',
            is_appealed=True,
            fine_reason='refund',
            fine_reason_id='2',
        )
        .run_by_id(fines_fixtures)
    )


async def test_not_found_fail(fines_fixtures):
    await (
        helper.OrderFinesTest()
        .on_request_by_id(fine_id='4')
        .should_fail(
            status=404, code='NOT_FOUND', message='Fine id == \'4\' not found',
        )
        .run_by_id(fines_fixtures)
    )


async def test_500_fail(fines_fixtures):
    await (
        helper.OrderFinesTest()
        .on_request_by_id(fine_id='notnumber')
        .should_fail(status=500, code='INTERNAL_ERROR')
        .run_by_id(fines_fixtures)
    )
