from typing import Optional

import discounts_match  # pylint: disable=E0401
import pytest

from tests_eats_discounts import common


def _prepare_response(response: dict) -> dict:
    fetch_results = response['fetch_results']
    fetch_results.sort(key=lambda item: item['fetched_data']['hierarchy_name'])
    for value in fetch_results:
        fetched_parameters = value.get('fetched_parameters', [])
        for fetched_parameters_item in fetched_parameters:
            products = fetched_parameters_item.get('products')
            if products is not None:
                products['values'].sort()
            fetched_parameters_item.get('product_sets', []).sort()
    return response


def _compare_responses(response: dict, expected_response: dict):
    assert _prepare_response(response) == _prepare_response(expected_response)


async def _check_fetch_discounts(
        client,
        request: dict,
        expected_status_code: int,
        expected_response: dict,
):
    response = await client.post(
        'v3/fetch-discounts/', request, headers=common.get_headers(),
    )

    assert response.status_code == expected_status_code, response.json()
    if expected_status_code == 200:
        _compare_responses(response.json(), expected_response)
    else:
        assert response.json() == expected_response


@pytest.mark.parametrize(
    'discounts_create_body_file, response_file_name',
    (
        pytest.param(
            'no_match_discounts_create_body.json',
            'no_match_response.json',
            id='no_match',
        ),
        pytest.param(
            'match_discounts_create_body.json',
            'match_response.json',
            id='match',
        ),
    ),
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    EATS_DISCOUNTS_DISCOUNTS_CREATE_SETTINGS={'max_discounts': 100500},
    EATS_DISCOUNTS_FETCH_DISCOUNTS_SETTINGS={'max_discounts': 100500},
)
async def test_v3_fetch_discounts_ok(
        client,
        pgsql,
        mocked_time,
        stq_runner,
        load_json,
        discounts_create_body_file: str,
        response_file_name: str,
):
    now = mocked_time.now()
    common.plan_task(common.TASK_ID, pgsql, now)
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json(discounts_create_body_file),
        common.TASK_ID,
        'finished',
    )

    await client.invalidate_caches(cache_names=['rules-match-cache'])

    await _check_fetch_discounts(
        client, load_json('request.json'), 200, load_json(response_file_name),
    )


@discounts_match.remove_hierarchies('yandex_menu_cashback')
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_v3_fetch_discounts_missing_hierarchy(client, load_json):
    await _check_fetch_discounts(
        client, load_json('request.json'), 400, load_json('response.json'),
    )


@pytest.mark.parametrize(
    'add_rules_data_file_name, response_file_name',
    (
        pytest.param(
            'several_exclusions_add_rules_data.json',
            'several_exclusions_response.json',
            id='several_exclusions',
        ),
        pytest.param(
            'no_exclusions_add_rules_data.json',
            'no_exclusions_response.json',
            id='no_exclusions',
        ),
        pytest.param(
            'exclusions_match_add_rules_data.json',
            'exclusions_match_response.json',
            id='exclusions',
        ),
    ),
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    EATS_DISCOUNTS_FETCH_DISCOUNTS_SETTINGS={'max_discounts': 4},
)
async def test_v3_fetch_discounts_exclusions_ok(
        client,
        load_json,
        add_rules,
        add_rules_data_file_name: str,
        response_file_name: str,
):
    await add_rules(load_json(add_rules_data_file_name))

    await client.invalidate_caches(cache_names=['rules-match-cache'])

    await _check_fetch_discounts(
        client, load_json('request.json'), 200, load_json(response_file_name),
    )


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    EATS_DISCOUNTS_DISCOUNTS_CREATE_SETTINGS={'max_discounts': 3},
    EATS_DISCOUNTS_FETCH_DISCOUNTS_SETTINGS={'max_discounts': 4},
)
async def test_v3_fetch_discounts_pagination(
        client, pgsql, mocked_time, stq_runner, load_json, add_rules,
):
    now = mocked_time.now()
    common.plan_task(common.TASK_ID, pgsql, now)
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json('discounts_create_body.json'),
        common.TASK_ID,
        'finished',
    )
    await add_rules(load_json('add_rules_data.json'))

    await client.invalidate_caches(cache_names=['rules-match-cache'])

    await _check_fetch_discounts(
        client, load_json('request_1.json'), 200, load_json('response_1.json'),
    )
    await _check_fetch_discounts(
        client, load_json('request_2.json'), 200, load_json('response_2.json'),
    )
    await _check_fetch_discounts(
        client, load_json('request_3.json'), 200, load_json('response_3.json'),
    )


@pytest.mark.parametrize(
    'max_tasks_count, min_places_in_task',
    (
        pytest.param(None, 3, id='no_task_few_places'),
        pytest.param(4, None, id='few_task_no_places'),
        pytest.param(1, 100, id='one_task_many_places'),
        pytest.param(100, 1, id='many_tasks_one_place'),
        pytest.param(5, 2, id='few_tasks_and_places'),
    ),
)
@pytest.mark.config(
    EATS_DISCOUNTS_DISCOUNTS_CREATE_SETTINGS={'max_discounts': 100500},
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
async def test_v3_fetch_discounts_async_settings(
        client,
        taxi_config,
        mocked_time,
        pgsql,
        load_json,
        stq_runner,
        add_rules,
        max_tasks_count: Optional[int],
        min_places_in_task: Optional[int],
):
    config = {'max_discounts': 100500, 'async_settings': {}}
    async_settings = {}
    if max_tasks_count is not None:
        async_settings['max_tasks_count'] = max_tasks_count

    if min_places_in_task is not None:
        async_settings['min_places_in_task'] = min_places_in_task
    config['async_settings'] = async_settings
    taxi_config.set(EATS_DISCOUNTS_FETCH_DISCOUNTS_SETTINGS=config)

    await common.init_bin_sets(client)

    now = mocked_time.now()
    common.plan_task(common.TASK_ID, pgsql, now)
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json('discounts_create_body.json'),
        common.TASK_ID,
        'finished',
    )
    await add_rules(load_json('add_rules_data.json'))

    await client.invalidate_caches()

    await _check_fetch_discounts(
        client, load_json('request.json'), 200, load_json('response.json'),
    )


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    EATS_DISCOUNTS_DISCOUNTS_CREATE_SETTINGS={'max_discounts': 3},
    EATS_DISCOUNTS_FETCH_DISCOUNTS_SETTINGS={'max_discounts': 3},
)
async def test_v3_fetch_discounts_max_fetched_items(
        client, pgsql, mocked_time, stq_runner, load_json, add_rules,
):
    now = mocked_time.now()
    common.plan_task(common.TASK_ID, pgsql, now)
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json('discounts_create_body.json'),
        common.TASK_ID,
        'finished',
    )
    await add_rules(load_json('add_rules_data.json'))

    await client.invalidate_caches()

    await _check_fetch_discounts(
        client, load_json('request.json'), 200, load_json('response.json'),
    )


@pytest.mark.parametrize(
    'max_discounts, response_file_name',
    (
        pytest.param(
            1, 'discount_not_fetched_response.json', id='discount_not_fetched',
        ),
        pytest.param(
            2, 'discount_fetched_response.json', id='discount_fetched',
        ),
    ),
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    EATS_DISCOUNTS_DISCOUNTS_CREATE_SETTINGS={'max_discounts': 3},
)
async def test_v3_fetch_discounts_max_discounts(
        client,
        pgsql,
        mocked_time,
        stq_runner,
        load_json,
        taxi_config,
        max_discounts: int,
        response_file_name: str,
):
    taxi_config.set(
        EATS_DISCOUNTS_FETCH_DISCOUNTS_SETTINGS={
            'max_discounts': max_discounts,
        },
    )

    now = mocked_time.now()
    common.plan_task(common.TASK_ID, pgsql, now)
    await common.partners_discounts_create(
        stq_runner,
        pgsql,
        load_json('discounts_create_body.json'),
        common.TASK_ID,
        'finished',
    )

    await client.invalidate_caches()

    await _check_fetch_discounts(
        client, load_json('request.json'), 200, load_json(response_file_name),
    )
