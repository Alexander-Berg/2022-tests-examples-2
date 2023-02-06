import pytest

from tests_eats_billing_processor.fines import helper


async def test_appeal_incorrect_data_fail(fines_fixtures, pgsql):
    await (
        helper.OrderFinesTest()
        .appeal_request(fine_id='1a', ticket='')
        .should_fail(400, 'INCORRECT_DATA', 'Incorrect fine id: "1a"')
        .appeal_run(fines_fixtures, pgsql)
    )


async def test_appeal_fine_not_found_fail(fines_fixtures, pgsql):
    await (
        helper.OrderFinesTest()
        .appeal_request(fine_id='1', ticket='')
        .should_fail(404, 'NOT_FOUND', 'Fine id == \'1\' not found')
        .appeal_run(fines_fixtures, pgsql)
    )


@pytest.mark.pgsql('eats_billing_processor', files=['fine_appeal.sql'])
async def test_appeal_happy_path(fines_fixtures, pgsql):
    await (
        helper.OrderFinesTest()
        .appeal_request(fine_id='2', ticket='EDA-1')
        .expect_appeal(fine_id='2', ticket='EDA-1', amount='300.00')
        .appeal_run(fines_fixtures, pgsql)
    )
