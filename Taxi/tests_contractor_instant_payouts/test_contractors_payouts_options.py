import pytest


async def test_ready(contractors_payouts_options, stock):
    response = await contractors_payouts_options()

    assert response.status_code == 200, response.text
    assert response.json() == {
        'status': 'ready',
        'amount_minimum': '10',
        'amount_maximum': '45',
        'fee_percent': '10',
        'fee_minimum': '1',
    }


async def test_not_available(contractors_payouts_options, stock):
    response = await contractors_payouts_options(
        contractor_id='48b7b5d81559460fb176693800000004',
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'status': 'not_available',
        'amount_minimum': '0',
        'amount_maximum': '0',
        'fee_percent': '0',
        'fee_minimum': '0',
    }


async def test_already_in_progress(contractors_payouts_options, stock):
    response = await contractors_payouts_options(
        contractor_id='48b7b5d81559460fb176693800000002',
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'status': 'already_in_progress',
        'amount_minimum': '0',
        'amount_maximum': '0',
        'fee_percent': '0',
        'fee_minimum': '0',
    }


@pytest.mark.now('2020-01-01T18:00:00+03:00')
async def test_daily_limit_exceeded(contractors_payouts_options, stock):
    response = await contractors_payouts_options(
        contractor_id='48b7b5d81559460fb176693800000003',
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'status': 'daily_limit_exceeded',
        'amount_minimum': '0',
        'amount_maximum': '0',
        'fee_percent': '0',
        'fee_minimum': '0',
    }
