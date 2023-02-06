import pytest

from eats_tips_payments.common import payments


@pytest.mark.parametrize(
    'transaction_id, expected_result', [(22, 600), (1, None)],
)
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
async def test_get_system_commission(web_app, transaction_id, expected_result):
    system_income = await payments._get_system_income(  # pylint: disable=W0212
        web_app['context'], transaction_id,
    )
    assert system_income == expected_result
