import discounts_match  # pylint: disable=E0401
import pytest

from tests_eats_discounts import common


def _prepare_response(response: dict) -> dict:
    for value in response.values():
        for discount in value['discounts']:
            discount['products']['values'].sort()
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
        'v2/fetch-discounts/', request, headers=common.get_headers(),
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
    EATS_DISCOUNTS_DISCOUNTS_CREATE_SETTINGS={'max_discounts': 3},
    EATS_DISCOUNTS_FETCH_DISCOUNTS_SETTINGS={'max_discounts': 3},
)
async def test_v2_fetch_discounts_ok(
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
async def test_v2_fetch_discounts_missing_hierarchy(client, load_json):
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
            id='no_exclusions',
        ),
    ),
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    EATS_DISCOUNTS_FETCH_DISCOUNTS_SETTINGS={'max_discounts': 4},
)
async def test_v2_fetch_discounts_exclusions_ok(
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
    EATS_DISCOUNTS_FETCH_DISCOUNTS_SETTINGS={'max_discounts': 3},
)
async def test_v2_fetch_discounts_pagination(
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
