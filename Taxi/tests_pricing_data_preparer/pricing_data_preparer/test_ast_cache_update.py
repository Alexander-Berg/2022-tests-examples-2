# pylint: disable=redefined-outer-name, import-only-modules
# flake8: noqa F401
import datetime
import pytest

from .plugins import utils_request
from .plugins.mock_user_api import mock_user_api_get_phones
from .plugins.mock_user_api import mock_user_api_get_users, user_api
from .plugins.mock_surge import surger, mock_surger
from .plugins.mock_ride_discounts import ride_discounts, mock_ride_discounts
from .plugins.mock_tags import tags, mock_tags


def add_rule(pgsql):
    rule = {
        'rule_id': '2',
        'name': '\'surge\'',
        'source_code': '\'return (1.1 / *ride.price) * ride.price;\'',
        'policy': '\'both_side\'',
        'author': '\'200ok draft\'',
        'ast': '\'CR(boarding=B(B(B(1.10000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(boarding)),distance=B(B(B(1.10000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(distance)),time=B(B(B(1.10000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(time)),waiting=B(B(B(1.10000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(waiting)),requirements=B(B(B(1.10000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(requirements)),transit_waiting=B(B(B(1.10000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(transit_waiting)),destination_waiting=B(B(B(1.10000,/,U(*,B(ride,.,F(price)))),*,B(ride,.,F(price))),.,F(destination_waiting)))\'',
        'updated': '\'5000-05-04 06:00:00\'',
        'pmv_task_id': '1',
    }
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            'DELETE FROM price_modifications.rules_drafts '
            'WHERE rule_id = 2',
        )
        cursor.execute(
            'UPDATE price_modifications.rules '
            'SET deleted = True '
            'WHERE rule_id = 10',
        )
        cursor.execute(
            f'INSERT INTO price_modifications.rules'
            f'({", ".join(rule.keys())}) '
            f'VALUES ({", ".join(rule.values())})',
        )


def update_workabilities(pgsql):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            'UPDATE price_modifications.workabilities '
            'SET rule_id = 2 '
            'WHERE rule_id = 10',
        )


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': True},
    PRICING_DATA_PREPARER_SURGER_ENABLED={
        '__default__': {'__default__': True},
    },
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True,
    PRICING_PASSENGER_TAGS_ENABLED=True,
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
@pytest.mark.filldb(tariff_settings='all_fixed')
@pytest.mark.parametrize(
    'invalidate_caches, expected_modifications, expected_rules_update_error',
    [
        ([], [10], False),
        (['pricing-rules-cache'], [10], True),
        (['price-modifications-cache'], [10], False),
        (['price-modifications-cache', 'pricing-rules-cache'], [2], False),
        (['pricing-rules-cache', 'price-modifications-cache'], [10], True),
    ],
    ids=[
        'no_updates',
        'modifications_workability_only_update',
        'ast_only_update',
        'ast_then_modifications_workability_update',
        'modifications_workability_then_ast_update',
    ],
)
async def test_ast_cache_update(
        taxi_pricing_data_preparer,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        surger,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        invalidate_caches,
        expected_modifications,
        pgsql,
        testpoint,
        expected_rules_update_error,
):
    # pylint: disable=invalid-name
    @testpoint('price_modification_rules_update_error')
    async def price_modification_rules_update_error(data):
        pass

    # Dry run to skip full update
    for cache_name in ('pricing-rules-cache', 'price-modifications-cache'):
        await taxi_pricing_data_preparer.invalidate_caches(
            clean_update=True, cache_names=[cache_name],
        )

    pre_request = utils_request.Request().set_categories(['econom'])
    request = pre_request.get()

    add_rule(pgsql)
    update_workabilities(pgsql)

    for cache_name in invalidate_caches:
        await taxi_pricing_data_preparer.invalidate_caches(
            clean_update=True, cache_names=[cache_name],
        )

    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200
    data = response.json()
    assert (
        data['categories']['econom']['user']['modifications']['for_fixed']
        == expected_modifications
    )
    if expected_rules_update_error:
        await price_modification_rules_update_error.wait_call()
    else:
        assert price_modification_rules_update_error.times_called == 0


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': True},
    PRICING_DATA_PREPARER_SURGER_ENABLED={
        '__default__': {'__default__': True},
    },
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True,
    PRICING_PASSENGER_TAGS_ENABLED=True,
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.pgsql(
    'pricing_data_preparer',
    files=['rules.sql', 'workabilities_with_unexistent_rule.sql'],
)
@pytest.mark.filldb(tariff_settings='all_fixed')
async def test_cache_with_unexistent_rules_initialization(
        taxi_pricing_data_preparer,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        surger,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
):
    pre_request = utils_request.Request().set_categories(['econom'])
    request = pre_request.get()

    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200
    data = response.json()
    assert data['categories']['econom']['user']['modifications'][
        'for_fixed'
    ] == [10]


@pytest.fixture
async def get_user_modifications(taxi_pricing_data_preparer):
    async def get_user_modifications_impl():
        pre_request = utils_request.Request().set_categories(['econom'])
        request = pre_request.get()

        response = await taxi_pricing_data_preparer.post(
            'v2/prepare', json=request,
        )
        return response.json()['categories']['econom']['user'][
            'modifications'
        ]['for_fixed']

    return get_user_modifications_impl


@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
async def test_modifications_asts_cache_update(
        taxi_pricing_data_preparer,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        surger,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        pgsql,
        load,
        get_user_modifications,
):
    def update_rule(old_id, new_id):
        with pgsql['pricing_data_preparer'].cursor() as cursor:
            cursor.execute(
                load('update_rules_workabilities.sql').format(
                    old_id=old_id,
                    new_id=new_id,
                    approvals_id=new_id,
                    name=f'new_rule_{new_id}',
                ),
            )

    async def invalidate_caches():
        await taxi_pricing_data_preparer.invalidate_caches(
            clean_update=False,
            cache_names=['price-modifications-cache', 'pricing-rules-cache'],
        )

    # We need to run cache invalidate to skip first full-update
    await invalidate_caches()

    update_rule(10, 42)
    assert (await get_user_modifications()) == [10]
    await invalidate_caches()
    assert (await get_user_modifications()) == [42]

    update_rule(42, 45)
    await invalidate_caches()
    assert (await get_user_modifications()) == [45]


@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
@pytest.mark.parametrize(
    'new_timestamp,expected_id',
    [('9000-01-01 00:00:00', 42), ('1000-01-01 00:00:00', 10)],
)
async def test_modifications_asts_cache_ignore_old_records(
        taxi_pricing_data_preparer,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        surger,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        pgsql,
        load,
        new_timestamp,
        expected_id,
        get_user_modifications,
):
    def update_rule(old_id, new_id, updated):
        with pgsql['pricing_data_preparer'].cursor() as cursor:
            cursor.execute(
                load('update_rules_workabilities_with_updated.sql').format(
                    old_id=old_id,
                    new_id=new_id,
                    approvals_id=new_id,
                    name=f'new_rule_{new_id}',
                    updated=updated,
                ),
            )

    async def invalidate_caches():
        await taxi_pricing_data_preparer.invalidate_caches(
            clean_update=False,
            cache_names=['price-modifications-cache', 'pricing-rules-cache'],
        )

    # We need to run cache invalidate to skip first full-update
    await invalidate_caches()

    update_rule(10, 42, new_timestamp)
    assert (await get_user_modifications()) == [10]
    await invalidate_caches()
    assert (await get_user_modifications()) == [expected_id]


@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
@pytest.mark.parametrize('updated_lag,expected_read', [(4, False), (2, True)])
async def test_modification_asts_correction(
        taxi_pricing_data_preparer,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        surger,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        pgsql,
        load,
        updated_lag,
        expected_read,
        get_user_modifications,
):
    def update_rule(old_id, new_id, updated):
        with pgsql['pricing_data_preparer'].cursor() as cursor:
            cursor.execute(
                load('update_rules_workabilities_with_updated.sql').format(
                    old_id=old_id,
                    new_id=new_id,
                    approvals_id=new_id,
                    name=f'new_rule_{new_id}',
                    updated=updated,
                ),
            )

    async def invalidate_caches():
        await taxi_pricing_data_preparer.invalidate_caches(
            clean_update=False,
            cache_names=['price-modifications-cache', 'pricing-rules-cache'],
        )

    # We need to run cache invalidate to skip first full-update
    await invalidate_caches()
    assert (await get_user_modifications()) == [10]

    new_timestamp = datetime.datetime.now() - datetime.timedelta(
        minutes=updated_lag,
    )
    update_rule(10, 42, new_timestamp.isoformat())
    await invalidate_caches()
    assert (await get_user_modifications()) == [42 if expected_read else 10]
