import pytest

from tests_driver_categories_api import category_utils

HANDLER_URI = 'v2/drivers/categories'
CATEGORIES = [['econom'], ['business', 'econom']]
DRIVER_ID = 'driver_1'
PARK_ID = 'park_1'


def _get_data_source_config(storage_type):
    return {
        'DRIVER_CATEGORIES_API_DATA_SOURCE_WRITE': {
            '/v2/drivers/categories POST': {'storage_type': storage_type},
            '__default__': {'storage_type': 'old_only'},
        },
    }


def _get_params_template_main(storage_type):
    return [
        pytest.param(
            CATEGORIES[0],
            'append',
            ['business', 'econom'],
            ['business'],
            storage_type,
            id=f'append 1 category, {storage_type}',
        ),
        pytest.param(
            CATEGORIES[1],
            'append',
            ['business', 'econom'],
            [],
            storage_type,
            id=f'append 2 categories, {storage_type}',
        ),
        pytest.param(
            CATEGORIES[0],
            'remove',
            ['business'],
            ['business', 'econom'],
            storage_type,
            id=f'remove 1 category, {storage_type}',
        ),
        pytest.param(
            CATEGORIES[1],
            'remove',
            ['business'],
            ['business', 'econom'],
            storage_type,
            id=f'remove 2 categories, {storage_type}',
        ),
        pytest.param(
            CATEGORIES[0],
            'replace',
            ['business'],
            [
                item
                for item in category_utils.get_all_restrictions()
                if item not in CATEGORIES[0]
            ],
            storage_type,
            id=f'replace 1 category, {storage_type}',
        ),
        pytest.param(
            CATEGORIES[1],
            'replace',
            ['business'],
            [
                item
                for item in category_utils.get_all_restrictions()
                if item not in CATEGORIES[1]
            ],
            storage_type,
            id=f'replace 2 categories, {storage_type}',
        ),
        pytest.param(
            CATEGORIES[0],
            'append',
            ['robot', 'chain', 'econom'],
            ['robot', 'chain'],
            storage_type,
            id=f'append 1 category, {storage_type}, initial legacy flags',
        ),
        pytest.param(
            CATEGORIES[1],
            'append',
            ['robot', 'chain', 'business', 'ultimate'],
            ['robot', 'chain', 'ultimate'],
            storage_type,
            id=f'append 2 categories, {storage_type}, initial legacy flags',
        ),
        pytest.param(
            CATEGORIES[0],
            'remove',
            ['robot', 'chain'],
            ['robot', 'chain', 'econom'],
            storage_type,
            id=f'remove 1 category, {storage_type}, initial legacy flags',
        ),
        pytest.param(
            CATEGORIES[1],
            'remove',
            ['robot', 'chain', 'business', 'ultimate'],
            ['robot', 'chain', 'econom', 'business', 'ultimate'],
            storage_type,
            id=f'remove 2 categories, {storage_type}, initial legacy flags',
        ),
        pytest.param(
            CATEGORIES[0],
            'replace',
            ['robot', 'chain', 'maybach'],
            [
                item
                for item in category_utils.get_all_restrictions()
                if item not in CATEGORIES[0]
            ]
            + ['robot', 'chain'],
            storage_type,
            id=f'replace 1 category, {storage_type}, initial legacy flags',
        ),
        pytest.param(
            CATEGORIES[1],
            'replace',
            ['robot', 'chain', 'business'],
            [
                item
                for item in category_utils.get_all_restrictions()
                if item not in CATEGORIES[1]
            ]
            + ['robot', 'chain'],
            storage_type,
            id=f'replace 2 categories, {storage_type}, initial legacy flags',
        ),
    ]


@pytest.mark.parametrize(
    'categories,merge_policy,initial_restrictions,expected_restrictions,'
    'storage_type',
    _get_params_template_main('old_only')
    + _get_params_template_main('old_and_pg')
    + _get_params_template_main('pg_only'),
)
@pytest.mark.pgsql(
    'driver-categories-api', files=['pg_driver-categories-api.sql'],
)
async def test_categories(
        taxi_driver_categories_api,
        stq,
        categories,
        merge_policy,
        initial_restrictions,
        expected_restrictions,
        storage_type,
        redis_store,
        pgsql,
        taxi_config,
):
    taxi_config.set_values(_get_data_source_config(storage_type))

    category_utils.set_redis_restrictions(
        redis_store, PARK_ID, DRIVER_ID, initial_restrictions,
    )
    category_utils.upsert_driver_restrictions(
        pgsql,
        PARK_ID,
        DRIVER_ID,
        category_utils.filter_legacy_flags(initial_restrictions),
    )

    response = await taxi_driver_categories_api.post(
        HANDLER_URI,
        params={'driver_id': DRIVER_ID, 'park_id': PARK_ID},
        json={
            'categories': [{'name': c} for c in categories],
            'merge_policy': merge_policy,
        },
    )
    assert response.status_code == 200

    assert stq.driver_categories_tag_maker.times_called == (
        storage_type != 'old_only'
    )

    expected_redis_restrictions = (
        expected_restrictions
        if storage_type != 'pg_only'
        else initial_restrictions
    )

    expected_pg_restrictions = (
        category_utils.filter_legacy_flags(expected_restrictions)
        if storage_type != 'old_only'
        else category_utils.filter_legacy_flags(initial_restrictions)
    )

    category_utils.check_pg_restrictions(
        pgsql,
        PARK_ID,
        DRIVER_ID,
        category_utils.filter_legacy_flags(expected_pg_restrictions),
    )
    category_utils.check_redis_restrictions(
        redis_store, PARK_ID, DRIVER_ID, expected_redis_restrictions,
    )


def _get_params_template_extra(merge_policy, storage_type, code):
    return [
        pytest.param(
            'econom',
            merge_policy,
            storage_type,
            code,
            id=f'{merge_policy} 1 category, {storage_type}',
        ),
    ]


@pytest.mark.parametrize(
    'categories,merge_policy,storage_type,code',
    _get_params_template_extra('append', 'old_only', 400)
    + _get_params_template_extra('append', 'old_and_pg', 400)
    + _get_params_template_extra('append', 'pg_only', 200)
    + _get_params_template_extra('remove', 'old_only', 400)
    + _get_params_template_extra('remove', 'old_and_pg', 400)
    + _get_params_template_extra('remove', 'pg_only', 200)
    + _get_params_template_extra('replace', 'old_only', 400)
    + _get_params_template_extra('replace', 'old_and_pg', 400)
    + _get_params_template_extra('replace', 'pg_only', 200),
)
@pytest.mark.redis_store(
    ['hset', 'RobotSettings:park_1:Settings', 'driver_1', 'INVALID DATA'],
    ['sadd', 'RobotSettings:park_1:Settings_64', 'driver_1'],
)
async def test_categories_with_invalid_data_in_redis(
        taxi_driver_categories_api,
        categories,
        merge_policy,
        storage_type,
        code,
        taxi_config,
):
    taxi_config.set_values(_get_data_source_config(storage_type))

    response = await taxi_driver_categories_api.post(
        HANDLER_URI,
        params={'driver_id': DRIVER_ID, 'park_id': PARK_ID},
        json={
            'categories': [{'name': c} for c in categories],
            'merge_policy': 'append',
        },
    )
    assert response.status_code == code
