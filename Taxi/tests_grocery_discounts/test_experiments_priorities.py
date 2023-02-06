import datetime
from typing import Optional

import pytest

from tests_grocery_discounts import common

EXPERIMENTS_URL = '/v3/admin/experiments'
EXPERIMENTS_CHECK_URL = '/v3/admin/experiments/check'


async def _get_experiments(taxi_eats_discounts, expected_body: dict) -> None:
    response = await taxi_eats_discounts.get(
        EXPERIMENTS_URL, headers=common.get_headers(),
    )
    assert response.status_code == 200, response.json()
    assert response.json() == expected_body


async def _post_experiments(
        taxi_eats_discounts,
        request: dict,
        expected_status_code: int = 200,
        expected_response: Optional[dict] = None,
) -> None:
    response = await taxi_eats_discounts.post(
        EXPERIMENTS_URL,
        request,
        headers=common.get_draft_headers('draft_id_test_admin_experiments'),
    )
    assert response.status_code == expected_status_code, response.json()
    if expected_status_code == 200:
        assert response.json() == request
    elif expected_response is not None:
        assert response.json() == expected_response


async def _post_experiments_check(
        taxi_eats_discounts,
        request: dict,
        expected_status_code: int = 200,
        expected_response: Optional[dict] = None,
) -> None:
    response = await taxi_eats_discounts.post(
        EXPERIMENTS_CHECK_URL, request, headers=common.get_headers(),
    )
    assert response.status_code == expected_status_code, response.json()
    if expected_status_code == 200:
        assert response.json() == {
            'change_doc_id': 'experiments',
            'data': request,
            'diff': {'current': {'experiments': []}, 'new': request},
        }
    elif expected_response is not None:
        assert response.json() == expected_response


@pytest.mark.servicetest
@pytest.mark.now('2020-07-19T08:00:00')
async def test_experiments(taxi_grocery_discounts, mocked_time):
    now = mocked_time.now()
    experiments_0 = {'experiments': []}
    await _get_experiments(taxi_grocery_discounts, experiments_0)

    experiments_1 = {'experiments': ['first', 'second']}
    await _post_experiments(taxi_grocery_discounts, experiments_1)
    await _get_experiments(taxi_grocery_discounts, experiments_1)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    await _post_experiments(taxi_grocery_discounts, experiments_0)
    await _get_experiments(taxi_grocery_discounts, experiments_0)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    experiments_2 = {'experiments': ['first', 'second', 'third']}
    await _post_experiments(taxi_grocery_discounts, experiments_2)
    await _get_experiments(taxi_grocery_discounts, experiments_2)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    experiments_3 = {'experiments': ['']}
    await _post_experiments(taxi_grocery_discounts, experiments_3, 400)
    await _get_experiments(taxi_grocery_discounts, experiments_2)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    await _post_experiments(taxi_grocery_discounts, experiments_0)
    await _get_experiments(taxi_grocery_discounts, experiments_0)


@pytest.mark.servicetest
@pytest.mark.now('2020-07-19T08:00:00')
async def test_experiments_check(taxi_grocery_discounts, mocked_time):
    now = mocked_time.now()
    experiments_0 = {'experiments': []}
    await _get_experiments(taxi_grocery_discounts, experiments_0)

    experiments_1 = {'experiments': ['first', 'second']}
    await _post_experiments_check(taxi_grocery_discounts, experiments_1)
    await _get_experiments(taxi_grocery_discounts, experiments_0)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    await _post_experiments_check(taxi_grocery_discounts, experiments_0)
    await _get_experiments(taxi_grocery_discounts, experiments_0)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    experiments_2 = {'experiments': ['first', 'second', 'third']}
    await _post_experiments_check(taxi_grocery_discounts, experiments_2)
    await _get_experiments(taxi_grocery_discounts, experiments_0)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    experiments_3 = {'experiments': ['']}
    await _post_experiments_check(taxi_grocery_discounts, experiments_3, 400)
    await _get_experiments(taxi_grocery_discounts, experiments_0)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    await _post_experiments_check(taxi_grocery_discounts, experiments_0)
    await _get_experiments(taxi_grocery_discounts, experiments_0)


@pytest.mark.parametrize(
    'hierarchy_name',
    (
        pytest.param('cart_discounts', id='cart_discounts'),
        pytest.param('menu_discounts', id='menu_discounts'),
        pytest.param(
            'payment_method_discounts', id='payment_method_discounts',
        ),
    ),
)
@pytest.mark.parametrize(
    'handler',
    (
        pytest.param(EXPERIMENTS_URL, id='experiments'),
        pytest.param(EXPERIMENTS_CHECK_URL, id='check_experiments'),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_experiments_references(
        taxi_grocery_discounts,
        mocked_time,
        handler: str,
        hierarchy_name: str,
        add_rules,
):
    experiments = {'experiments': ['first', 'second']}
    await _post_experiments(taxi_grocery_discounts, experiments)
    await taxi_grocery_discounts.invalidate_caches()

    now = mocked_time.now()
    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)

    add_rules_data = common.get_add_rules_data()
    add_rules_data[hierarchy_name][0]['rules'].append(
        {'condition_name': 'experiment', 'values': ['first']},
    )
    await add_rules(add_rules_data)

    now = mocked_time.now()
    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)

    experiments = {'experiments': ['second']}
    expected_response = {
        'code': 'Validation error',
        'message': (
            'Some of entity values are used in possibly active discounts: '
            '{"condition_name":"experiment","values":["first"]}'
        ),
    }

    await taxi_grocery_discounts.invalidate_caches()
    if handler == EXPERIMENTS_URL:
        await _post_experiments(
            taxi_grocery_discounts, experiments, 400, expected_response,
        )
    else:
        await _post_experiments_check(
            taxi_grocery_discounts, experiments, 400, expected_response,
        )
