import pytest

from discounts_operation_calculations.internals import helpers


@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_suggests.sql'],
)
async def test_get_active_cities(cron_context):
    active_discounts = await helpers.ActiveDiscounts.retrieve_active_discounts(
        cron_context,
    )
    assert ['Санкт-Петербург'] == active_discounts.get_active_cities(
        algo_name='kt3', with_push=False, is_exp=False,
    )
    assert ['Йошкар-Ола'] == active_discounts.get_active_cities(
        algo_name='kt4', with_push=False, is_exp=True,
    )
    assert ['Йошкар-Ола'] == active_discounts.get_active_cities(
        algo_name='test', with_push=False, is_exp=True,
    )
    assert ['Миасс'] == active_discounts.get_active_cities(
        algo_name='kt5', with_push=True, is_exp=False,
    )
    assert ['Нижний Тагил'] == active_discounts.get_active_cities(
        algo_name='test2', with_push=False, is_exp=True,
    )
    assert ['Нижний Тагил'] == active_discounts.get_active_cities(
        algo_name='kt6', with_push=True, is_exp=True,
    )
    # check false positives
    assert [] == active_discounts.get_active_cities(
        algo_name='test2', with_push=True, is_exp=True,
    )
    assert [] == active_discounts.get_active_cities(
        algo_name='kt6', with_push=False, is_exp=True,
    )
    assert [] == active_discounts.get_active_cities(
        algo_name='kt6', with_push=True, is_exp=False,
    )
    assert [] == active_discounts.get_active_cities(
        algo_name='kt6', with_push=False, is_exp=False,
    )
    assert [] == active_discounts.get_active_cities(
        algo_name='kt3', with_push=True, is_exp=False,
    )
