import copy
import datetime
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_grocery_marketing import common


def _common_search_rules_conditions(
        conditions: List[dict], new_end_time: str,
) -> List[dict]:
    conditions = copy.deepcopy(conditions)
    for condition in conditions:
        if condition['condition_name'] == 'active_period':
            condition['values'][0]['end'] = new_end_time + '+00:00'
            break
    return conditions


def _common_search_rules_expected_data(new_end_time: str) -> dict:
    active_period: dict = copy.deepcopy(common.VALID_ACTIVE_PERIOD)
    active_period['values'][0]['end'] = new_end_time + '+00:00'

    result: dict = {'menu_tags': []}
    start = datetime.datetime.strptime(
        active_period['values'][0]['start'], common.DATETIME_FORMAT,
    )
    end = datetime.datetime.strptime(
        active_period['values'][0]['end'], common.DATETIME_FORMAT,
    )
    if start >= end:
        return result

    result['menu_tags'].append(
        {
            'tag': (
                common.get_added_tag(common.get_add_rules_data(), 'menu_tags')
            ),
            'match_path': (
                common.menu_match_path(active_period)['match_path']
            ),
            'meta_info': {
                'create_draft_id': 'draft_id_check_add_rules_validation',
                'end_time_draft_id': 'draft_id_change_rules_end_time',
            },
        },
    )

    return result


def _get_revision(hierarchy_name: str, pgsql) -> int:
    pg_cursor = pgsql['grocery_marketing'].cursor()
    pg_cursor.execute(
        f"""SELECT MAX(__revision)
            FROM
            grocery_marketing.match_rules_{hierarchy_name};""",
    )
    return list(pg_cursor)[0][0]


async def _change_rules_end_time_check(
        taxi_grocery_marketing,
        pgsql,
        hierarchy_name: str,
        conditions: List[dict],
        new_end_time: str,
        expected_status_code: int,
        expected_response: Optional[dict],
        no_match_expected: bool,
) -> List[int]:
    start_revision = _get_revision(hierarchy_name, pgsql)

    request: dict = {
        'hierarchy_name': hierarchy_name,
        'conditions': conditions,
        'new_end_time': new_end_time,
    }

    headers = common.get_headers()
    response = await taxi_grocery_marketing.post(
        common.CHANGE_RULES_END_TIME_CHECK_URL, request, headers=headers,
    )
    assert response.status_code == expected_status_code
    end_revision = _get_revision(hierarchy_name, pgsql)

    assert end_revision == start_revision
    if expected_status_code != 200:
        if expected_response is not None:
            assert response.json() == expected_response
        return []

    response_json = response.json()
    response_revisions: List[int] = sorted(response_json['data']['revisions'])
    assert bool(response_revisions) != no_match_expected

    response_lock_ids: List[dict] = response_json['lock_ids']
    lock_ids = [int(lock_id['id']) for lock_id in response_lock_ids]
    assert sorted(lock_ids) == response_revisions
    del response_json['data']['revisions']
    del response_json['lock_ids']

    data: dict = {
        'hierarchy_name': hierarchy_name,
        'conditions': conditions,
        'new_end_time': new_end_time,
    }
    assert response_json == {'data': data}
    return response_revisions


@pytest.mark.parametrize(
    'add_rules_data, conditions, hierarchy_name, new_end_time,'
    'expected_status_code, expected_response, no_match_expected',
    (
        pytest.param(
            common.get_add_rules_data(),
            common.get_add_rules_data()['menu_tags'][0]['rules'],
            'menu_tags',
            '2020-01-01T08:00:00',
            200,
            None,
            False,
            id='end_time_before_start_menu_tags',
        ),
        pytest.param(
            common.get_add_rules_data(),
            [
                {'condition_name': 'city', 'values': ['213']},
                {'condition_name': 'country', 'values': ['some_country']},
                {'condition_name': 'depot', 'values': ['some_depot']},
            ],
            'menu_tags',
            '2020-01-01T09:00:02',
            400,
            {
                'code': 'Validation error',
                'message': 'Rules must contain active_period field',
            },
            False,
            id='no_active_period',
        ),
    ),
)
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_change_rules_end_time_check(
        taxi_grocery_marketing,
        pgsql,
        hierarchy_name: str,
        add_rules_data: Dict[str, List[dict]],
        conditions: List[dict],
        new_end_time: str,
        expected_status_code: int,
        expected_response: Optional[dict],
        no_match_expected: bool,
):
    await common.add_rules(taxi_grocery_marketing, pgsql, add_rules_data)

    await _change_rules_end_time_check(
        taxi_grocery_marketing,
        pgsql,
        hierarchy_name,
        conditions,
        new_end_time,
        expected_status_code,
        expected_response,
        no_match_expected,
    )


@pytest.mark.parametrize(
    'add_rules_data, revisions, conditions, hierarchy_name, new_end_time,'
    'expected_status_code, expected_response, change_expected,'
    'no_match_expected',
    (
        pytest.param(
            common.get_add_rules_data(),
            None,
            common.get_add_rules_data()['menu_tags'][0]['rules'],
            'menu_tags',
            '2020-01-01T09:00:00',
            200,
            None,
            True,
            False,
            id='end_time_before_start_menu_tags',
        ),
        pytest.param(
            common.get_add_rules_data(),
            [],
            [
                {'condition_name': 'city', 'values': ['213']},
                {'condition_name': 'country', 'values': ['some_country']},
                {'condition_name': 'depot', 'values': ['some_depot']},
            ],
            'menu_tags',
            '2020-01-01T09:00:02',
            400,
            {
                'code': 'Validation error',
                'message': 'Rules must contain active_period field',
            },
            False,
            True,
            id='no_active_period',
        ),
    ),
)
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_change_rules_end_time(
        taxi_grocery_marketing,
        pgsql,
        revisions: Optional[List[int]],
        hierarchy_name: str,
        add_rules_data: Dict[str, List[dict]],
        conditions: List[dict],
        new_end_time: str,
        expected_status_code: int,
        expected_response: Optional[dict],
        change_expected: bool,
        no_match_expected: bool,
):
    await common.add_rules(taxi_grocery_marketing, pgsql, add_rules_data)

    start_revision = common.get_revision(pgsql)

    if revisions is None:
        if expected_status_code == 200:
            revisions = await _change_rules_end_time_check(
                taxi_grocery_marketing,
                pgsql,
                hierarchy_name,
                conditions,
                new_end_time,
                200,
                None,
                no_match_expected,
            )
        else:
            await _change_rules_end_time_check(
                taxi_grocery_marketing,
                pgsql,
                hierarchy_name,
                conditions,
                new_end_time,
                expected_status_code,
                expected_response,
                no_match_expected,
            )
            return

    if expected_status_code == 200:
        assert change_expected == bool(revisions)

    request: dict = {
        'hierarchy_name': hierarchy_name,
        'conditions': conditions,
        'new_end_time': new_end_time,
        'revisions': revisions,
    }

    headers = common.get_draft_headers('draft_id_change_rules_end_time')
    response = await taxi_grocery_marketing.post(
        common.CHANGE_RULES_END_TIME_URL, request, headers=headers,
    )
    assert response.status_code == expected_status_code
    end_revision = common.get_revision(pgsql)

    assert end_revision == start_revision

    if expected_status_code != 200:
        if expected_response is not None:
            assert response.json() == expected_response
        return

    assert response.json() == {}
    if new_end_time == '2020-01-01T09:00:00':
        new_end_time = '2020-01-01T09:00:01'
    if change_expected:
        await common.check_search_rules(
            taxi_grocery_marketing,
            hierarchy_name,
            _common_search_rules_conditions(conditions, new_end_time),
            1,
            None,
            _common_search_rules_expected_data(new_end_time),
            200,
        )


@pytest.mark.parametrize(
    'add_rules_data, conditions, hierarchy_name, add_rules_time, '
    'close_rules_time, new_end_time, expected_status_code, '
    'expected_response, no_match_expected',
    (
        pytest.param(
            common.get_add_rules_data(),
            common.get_add_rules_data()['menu_tags'][0]['rules'],
            'menu_tags',
            '2020-01-01T00:00:00+00:00',
            '2020-01-01T11:00:00+00:00',
            '2020-01-01T10:00:00',
            400,
            None,
            False,
            id='end_time_before_now',
        ),
        pytest.param(
            common.get_add_rules_data(),
            common.get_add_rules_data()['menu_tags'][0]['rules'],
            'menu_tags',
            '2020-01-01T00:00:00+00:00',
            '2020-01-01T07:00:00+00:00',
            '2020-01-01T10:03:00',
            400,
            None,
            False,
            id='end_time_before_now_plus_min_time_validation',
        ),
    ),
)
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
async def test_change_rules_end_time_check_by_now(
        taxi_grocery_marketing,
        pgsql,
        mocked_time,
        hierarchy_name: str,
        add_rules_data: Dict[str, List[dict]],
        conditions: List[dict],
        add_rules_time: str,
        close_rules_time: str,
        new_end_time: str,
        expected_status_code: int,
        expected_response: Optional[dict],
        no_match_expected: bool,
):
    mocked_time.set(datetime.datetime.fromisoformat(add_rules_time))
    await common.add_rules(taxi_grocery_marketing, pgsql, add_rules_data)

    mocked_time.set(datetime.datetime.fromisoformat(close_rules_time))
    await _change_rules_end_time_check(
        taxi_grocery_marketing,
        pgsql,
        hierarchy_name,
        conditions,
        new_end_time,
        expected_status_code,
        expected_response,
        no_match_expected,
    )


@pytest.mark.parametrize(
    'add_rules_data, count, conditions, new_end_time, ' 'hierarchy_name',
    (
        pytest.param(
            common.get_add_rules_data(
                hierarchy_names=frozenset(['menu_tags']),
            ),
            2,
            common.get_add_rules_data()['menu_tags'][0]['rules'],
            '2020-01-01T09:00:01',
            'menu_tags',
            id='menu_tags',
        ),
    ),
)
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_change_rules_end_time_duplicate(
        taxi_grocery_marketing,
        pgsql,
        hierarchy_name: str,
        add_rules_data: Dict[str, List[dict]],
        count: int,
        conditions: List[dict],
        new_end_time: str,
):
    for _ in range(count):
        await common.add_rules(taxi_grocery_marketing, pgsql, add_rules_data)

        revisions = await _change_rules_end_time_check(
            taxi_grocery_marketing,
            pgsql,
            hierarchy_name,
            conditions,
            new_end_time,
            200,
            None,
            False,
        )

        request: dict = {
            'hierarchy_name': hierarchy_name,
            'conditions': conditions,
            'new_end_time': new_end_time,
            'revisions': revisions,
        }
        headers = common.get_draft_headers()
        response = await taxi_grocery_marketing.post(
            common.CHANGE_RULES_END_TIME_URL, request, headers=headers,
        )
        assert response.status_code == 200

        assert response.json() == {}
