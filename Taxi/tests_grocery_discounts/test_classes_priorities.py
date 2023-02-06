import datetime
import json
from typing import Optional

import pytest

from tests_grocery_discounts import common

CLASSES_CHECK_URL = '/v3/admin/classes/check'


async def _get_classes(taxi_grocery_discounts, expected_body: dict) -> None:
    response = await taxi_grocery_discounts.get(
        common.CLASSES_URL, headers=common.get_headers(),
    )
    assert response.status_code == 200
    assert response.json() == expected_body


async def _post_classes_check(
        taxi_grocery_discounts,
        request: dict,
        expected_status_code: int = 200,
        expected_response: Optional[dict] = None,
) -> None:
    response = await taxi_grocery_discounts.post(
        CLASSES_CHECK_URL, request, headers=common.get_headers(),
    )
    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        assert response.json() == {
            'change_doc_id': 'classes',
            'data': request,
            'diff': {'current': {'classes': []}, 'new': request},
        }
    elif expected_response is not None:
        assert response.json() == expected_response


@pytest.mark.servicetest
@pytest.mark.pgsql('grocery_discounts', files=['init_discounts_db.sql'])
@pytest.mark.now('2020-07-19T08:00:00')
async def test_save_classes(taxi_grocery_discounts):
    response = await taxi_grocery_discounts.get(
        common.CLASSES_URL, headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'classes': ['second', 'third']}

    response = await taxi_grocery_discounts.post(
        common.CLASSES_URL,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
        data=json.dumps({'classes': ['first', 'second', 'third']}),
    )
    assert response.status_code == 200
    assert response.json() == {'classes': ['first', 'second', 'third']}

    response = await taxi_grocery_discounts.get(
        common.CLASSES_URL, headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'classes': ['first', 'second', 'third']}


@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_classes(taxi_grocery_discounts, mocked_time):
    now = mocked_time.now()
    classes_0 = {'classes': []}
    await _get_classes(taxi_grocery_discounts, classes_0)

    classes_1 = {'classes': ['first', 'second']}
    await common.set_classes(taxi_grocery_discounts, classes_1)
    await _get_classes(taxi_grocery_discounts, classes_1)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    await common.set_classes(taxi_grocery_discounts, classes_0)
    await _get_classes(taxi_grocery_discounts, classes_0)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    classes_2 = {'classes': ['first', 'second', 'third']}
    await common.set_classes(taxi_grocery_discounts, classes_2)
    await _get_classes(taxi_grocery_discounts, classes_2)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    classes_3 = {'classes': ['']}
    await common.set_classes(taxi_grocery_discounts, classes_3, 400)
    await _get_classes(taxi_grocery_discounts, classes_2)


@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_classes_check(taxi_grocery_discounts, mocked_time):
    now = mocked_time.now()
    classes_0 = {'classes': []}
    await _get_classes(taxi_grocery_discounts, classes_0)

    classes_1 = {'classes': ['first', 'second']}
    await _post_classes_check(taxi_grocery_discounts, classes_1)
    await _get_classes(taxi_grocery_discounts, classes_0)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    await _post_classes_check(taxi_grocery_discounts, classes_0)
    await _get_classes(taxi_grocery_discounts, classes_0)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    classes_2 = {'classes': ['first', 'second', 'third']}
    await _post_classes_check(taxi_grocery_discounts, classes_2)
    await _get_classes(taxi_grocery_discounts, classes_0)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    classes_3 = {'classes': ['']}
    await _post_classes_check(taxi_grocery_discounts, classes_3, 400)
    await _get_classes(taxi_grocery_discounts, classes_0)


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
        pytest.param(common.CLASSES_URL, id='classes'),
        pytest.param(CLASSES_CHECK_URL, id='check_classes'),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_classes_references(
        taxi_grocery_discounts,
        mocked_time,
        handler: str,
        hierarchy_name: str,
        add_rules,
):
    classes = {'classes': ['first', 'second']}
    await common.set_classes(taxi_grocery_discounts, classes)

    now = mocked_time.now()
    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)

    add_rules_data = common.get_add_rules_data()
    add_rules_data[hierarchy_name][0]['rules'].append(
        {'condition_name': 'class', 'values': ['first']},
    )
    await add_rules(add_rules_data)

    now = mocked_time.now()
    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)

    classes = {'classes': ['second']}
    expected_response = {
        'code': 'Validation error',
        'message': (
            'Some of entity values are used in possibly active discounts: '
            '{"condition_name":"class","values":["first"]}'
        ),
    }

    await taxi_grocery_discounts.invalidate_caches()
    if handler == common.CLASSES_URL:
        await common.set_classes(
            taxi_grocery_discounts, classes, 400, expected_response,
        )
    else:
        await _post_classes_check(
            taxi_grocery_discounts, classes, 400, expected_response,
        )
