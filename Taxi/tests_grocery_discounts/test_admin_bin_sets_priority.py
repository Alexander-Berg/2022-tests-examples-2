import http
import json
from typing import List
from typing import Optional

import pytest

from tests_grocery_discounts import common

BIN_SETS_PRIORITY_CHECK_URL = '/v3/admin/bin-sets-priority/check'


async def _get_bin_sets_priority(
        taxi_grocery_discounts,
        expected_body: Optional[dict],
        expected_status_code: int = 200,
) -> None:
    response = await taxi_grocery_discounts.get(
        common.BIN_SETS_PRIORITY_URL, headers=common.get_headers(),
    )
    assert response.status_code == expected_status_code
    if expected_body is not None:
        assert response.json() == expected_body


async def _post_bin_sets_priority_check(
        taxi_grocery_discounts,
        request: dict,
        expected_body: Optional[dict],
        expected_status_code: int = 200,
) -> None:
    response = await taxi_grocery_discounts.post(
        BIN_SETS_PRIORITY_CHECK_URL, request, headers=common.get_headers(),
    )
    assert response.status_code == expected_status_code
    if expected_body is not None:
        assert response.json() == expected_body


@pytest.mark.servicetest
@pytest.mark.pgsql('grocery_discounts', files=['init_discounts_db.sql'])
@pytest.mark.now('2020-07-15T08:00:00')
@pytest.mark.parametrize(
    'body, expected_status_code, expected_content',
    (
        (
            {'bin_set_names': ['Красивые', 'Любимое', 'Кофеманы']},
            http.HTTPStatus.OK,
            {
                'change_doc_id': 'bin-sets-priorities',
                'diff': {
                    'current': {'bin_set_names': ['Любимое', 'Красивые']},
                    'new': {
                        'bin_set_names': ['Красивые', 'Любимое', 'Кофеманы'],
                    },
                },
            },
        ),
        (
            {'bin_set_names': ['Красивые', 'Любимое']},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'Validation error',
                'message': (
                    'Not all active bin sets provided.' ' Check all bin sets.'
                ),
            },
        ),
        (
            {'bin_set_names': ['Красивые', 'Любимое', 'Красивые']},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'Validation error',
                'message': 'Provided duplicate bin sets to save: Красивые',
            },
        ),
        (
            {'bin_set_names': ['Красивые', 'Любимое', 'Нет такой группы']},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'Validation error',
                'message': (
                    'Bin set Нет такой группы '
                    'is not active or missing. '
                    'Check all bin sets.'
                ),
            },
        ),
        (
            {'bin_set_names': ['Красивые', 'Кофеманы', 'Прошла']},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'Validation error',
                'message': (
                    'Bin set Прошла is not active'
                    ' or missing. Check all bin sets.'
                ),
            },
        ),
    ),
)
@pytest.mark.parametrize(
    'url', [common.BIN_SETS_PRIORITY_URL, BIN_SETS_PRIORITY_CHECK_URL],
)
async def test_change_bin_sets_orders(
        taxi_grocery_discounts,
        body,
        expected_status_code,
        expected_content,
        url,
):

    response = await taxi_grocery_discounts.post(
        url, headers=common.DEFAULT_DISCOUNTS_HEADERS, data=json.dumps(body),
    )

    if expected_status_code == http.HTTPStatus.OK:
        if 'check' in url:
            expected_content['data'] = body
        else:
            expected_content = body

    assert response.status_code == expected_status_code, response.json()
    assert response.json() == expected_content

    if expected_status_code == http.HTTPStatus.OK:
        if 'check' not in url:
            response = await taxi_grocery_discounts.get(
                common.BIN_SETS_PRIORITY_URL,
                headers=common.DEFAULT_DISCOUNTS_HEADERS,
            )
            assert (
                response.status_code == expected_status_code
            ), response.json()
            assert (
                response.json()['active_bin_sets']
                == expected_content['bin_set_names']
            )


@pytest.mark.servicetest
@pytest.mark.pgsql('grocery_discounts', files=['init_discounts_db.sql'])
@pytest.mark.now('2020-07-15T08:00:00')
async def test_get_inactive_bins(taxi_grocery_discounts):
    response = await taxi_grocery_discounts.get(
        common.BIN_SETS_PRIORITY_URL, headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'active_bin_sets': ['Любимое', 'Красивые'],
        'old_bin_sets': ['Прошла', 'Кофеманы'],
    }


@pytest.mark.parametrize(
    'old_added',
    (
        pytest.param(True, id='old_added'),
        pytest.param(False, id='old_not_added'),
    ),
)
@pytest.mark.parametrize(
    'active_added',
    (
        pytest.param(True, id='active_added'),
        pytest.param(False, id='active_not_added'),
    ),
)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_bin_sets_priority_get(
        taxi_grocery_discounts, old_added: bool, active_added: bool,
):
    if old_added:
        await common.add_bin_set(
            taxi_grocery_discounts,
            {
                'name': 'old_bin_set',
                'time': {
                    'start': '2019-01-01T00:00:01',
                    'end': '2019-01-01T00:00:03',
                },
                'bins': [1],
            },
        )
    if active_added:
        await common.add_bin_set(
            taxi_grocery_discounts,
            {
                'name': 'bin_set',
                'time': {
                    'start': '2020-01-01T00:00:01',
                    'end': '2020-01-01T00:00:03',
                },
                'bins': [1],
            },
        )

    active_bin_sets: List[str] = []
    if active_added:
        active_bin_sets.append('bin_set')

    old_bin_sets = []
    if old_added:
        old_bin_sets.append('old_bin_set')
    await _get_bin_sets_priority(
        taxi_grocery_discounts,
        {'active_bin_sets': active_bin_sets, 'old_bin_sets': old_bin_sets},
        200,
    )


@pytest.mark.parametrize(
    'data, expected_body, expected_status_code',
    (
        pytest.param(
            {'bin_set_names': ['bin_set1', 'bin_set2', 'bin_set3']},
            {'bin_set_names': ['bin_set1', 'bin_set2', 'bin_set3']},
            200,
            id='all_active',
        ),
        pytest.param(
            {'bin_set_names': []},
            {
                'code': 'Validation error',
                'message': (
                    'Not all active bin sets provided. Check all bin sets.'
                ),
            },
            400,
            id='empty_sets_names',
        ),
        pytest.param(
            {'bin_set_names': ['bin_set1']},
            {
                'code': 'Validation error',
                'message': (
                    'Not all active bin sets provided. Check all bin sets.'
                ),
            },
            400,
            id='not_all_active',
        ),
        pytest.param(
            {
                'bin_set_names': [
                    'bin_set1',
                    'bin_set2',
                    'bin_set3',
                    'bin_set4',
                ],
            },
            {
                'code': 'Validation error',
                'message': (
                    'Not all active bin sets provided. Check all bin sets.'
                ),
            },
            400,
            id='too_much_bin_sets',
        ),
        pytest.param(
            {'bin_set_names': ['bin_set1', 'bin_set3', 'bin_set3']},
            {
                'code': 'Validation error',
                'message': 'Provided duplicate bin sets to save: bin_set3',
            },
            400,
            id='duplicate_bin_set',
        ),
        pytest.param(
            {'bin_set_names': ['bin_set1', 'bin_set2', 'old_bin_set']},
            {
                'code': 'Validation error',
                'message': (
                    'Bin set old_bin_set is not active or missing. '
                    'Check all bin sets.'
                ),
            },
            400,
            id='excessive_bin_set',
        ),
        pytest.param(
            {'bin_set_names': ['bin_set1', 'bin_set2', 'bin_set4']},
            {
                'code': 'Validation error',
                'message': (
                    'Bin set bin_set4 is not active or missing. '
                    'Check all bin sets.'
                ),
            },
            400,
            id='missing_bin_set',
        ),
        pytest.param(
            {'bin_set_names': ['bin_set3', 'bin_set2', 'bin_set1']},
            {'bin_set_names': ['bin_set3', 'bin_set2', 'bin_set1']},
            200,
            id='all_active_reverse',
        ),
    ),
)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_bin_sets_priority(
        taxi_grocery_discounts,
        data: dict,
        expected_body: Optional[dict],
        expected_status_code: int,
):
    await common.add_bin_set(
        taxi_grocery_discounts,
        {
            'name': 'old_bin_set',
            'time': {
                'start': '2019-01-01T00:00:01',
                'end': '2019-01-01T00:00:03',
            },
            'bins': [1],
        },
    )

    await common.add_bin_set(
        taxi_grocery_discounts,
        {
            'name': 'bin_set1',
            'time': {
                'start': '2020-01-01T00:00:01',
                'end': '2020-01-01T00:00:03',
            },
            'bins': [1],
        },
    )

    await common.add_bin_set(
        taxi_grocery_discounts,
        {
            'name': 'bin_set2',
            'time': {
                'start': '2020-01-01T00:00:01',
                'end': '2020-01-01T00:00:03',
            },
            'bins': [1],
        },
    )

    await common.add_bin_set(
        taxi_grocery_discounts,
        {
            'name': 'bin_set3',
            'time': {
                'start': '2020-01-01T00:00:01',
                'end': '2020-01-01T00:00:03',
            },
            'bins': [1],
        },
    )
    initial_order = {'bin_set_names': ['bin_set1', 'bin_set2', 'bin_set3']}
    await common.set_bin_sets_priority(taxi_grocery_discounts, initial_order)

    await common.set_bin_sets_priority(
        taxi_grocery_discounts, data, expected_body, expected_status_code,
    )
    order = (
        expected_body['bin_set_names']
        if expected_status_code == 200 and expected_body is not None
        else initial_order['bin_set_names']
    )

    await _get_bin_sets_priority(
        taxi_grocery_discounts,
        {'active_bin_sets': order, 'old_bin_sets': ['old_bin_set']},
        200,
    )


@pytest.mark.parametrize(
    'data, expected_body, expected_status_code',
    (
        pytest.param(
            {'bin_set_names': ['bin_set1', 'bin_set2', 'bin_set3']},
            {
                'change_doc_id': 'bin-sets-priorities',
                'data': {
                    'bin_set_names': ['bin_set1', 'bin_set2', 'bin_set3'],
                },
                'diff': {
                    'current': {
                        'bin_set_names': ['bin_set1', 'bin_set2', 'bin_set3'],
                    },
                    'new': {
                        'bin_set_names': ['bin_set1', 'bin_set2', 'bin_set3'],
                    },
                },
            },
            200,
            id='all_active',
        ),
        pytest.param(
            {'bin_set_names': []},
            {
                'code': 'Validation error',
                'message': (
                    'Not all active bin sets provided. Check all bin sets.'
                ),
            },
            400,
            id='empty_sets_names',
        ),
        pytest.param(
            {'bin_set_names': ['bin_set1']},
            {
                'code': 'Validation error',
                'message': (
                    'Not all active bin sets provided. Check all bin sets.'
                ),
            },
            400,
            id='not_all_active',
        ),
        pytest.param(
            {
                'bin_set_names': [
                    'bin_set1',
                    'bin_set2',
                    'bin_set3',
                    'bin_set4',
                ],
            },
            {
                'code': 'Validation error',
                'message': (
                    'Not all active bin sets provided. Check all bin sets.'
                ),
            },
            400,
            id='too_much_bin_sets',
        ),
        pytest.param(
            {'bin_set_names': ['bin_set1', 'bin_set3', 'bin_set3']},
            {
                'code': 'Validation error',
                'message': 'Provided duplicate bin sets to save: bin_set3',
            },
            400,
            id='duplicate_bin_set',
        ),
        pytest.param(
            {'bin_set_names': ['bin_set1', 'bin_set2', 'old_bin_set']},
            {
                'code': 'Validation error',
                'message': (
                    'Bin set old_bin_set is not active or missing. '
                    'Check all bin sets.'
                ),
            },
            400,
            id='excessive_bin_set',
        ),
        pytest.param(
            {'bin_set_names': ['bin_set1', 'bin_set2', 'bin_set4']},
            {
                'code': 'Validation error',
                'message': (
                    'Bin set bin_set4 is not active or missing. '
                    'Check all bin sets.'
                ),
            },
            400,
            id='missing_bin_set',
        ),
        pytest.param(
            {'bin_set_names': ['bin_set3', 'bin_set2', 'bin_set1']},
            {
                'change_doc_id': 'bin-sets-priorities',
                'data': {
                    'bin_set_names': ['bin_set3', 'bin_set2', 'bin_set1'],
                },
                'diff': {
                    'current': {
                        'bin_set_names': ['bin_set1', 'bin_set2', 'bin_set3'],
                    },
                    'new': {
                        'bin_set_names': ['bin_set3', 'bin_set2', 'bin_set1'],
                    },
                },
            },
            200,
            id='all_active_reverse',
        ),
    ),
)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_bin_sets_priority_check(
        taxi_grocery_discounts,
        data: dict,
        expected_body: Optional[dict],
        expected_status_code: int,
):
    await common.add_bin_set(
        taxi_grocery_discounts,
        {
            'name': 'old_bin_set',
            'time': {
                'start': '2019-01-01T00:00:01',
                'end': '2019-01-01T00:00:03',
            },
            'bins': [1],
        },
    )

    await common.add_bin_set(
        taxi_grocery_discounts,
        {
            'name': 'bin_set1',
            'time': {
                'start': '2020-01-01T00:00:01',
                'end': '2020-01-01T00:00:03',
            },
            'bins': [1],
        },
    )

    await common.add_bin_set(
        taxi_grocery_discounts,
        {
            'name': 'bin_set2',
            'time': {
                'start': '2020-01-01T00:00:01',
                'end': '2020-01-01T00:00:03',
            },
            'bins': [1],
        },
    )

    await common.add_bin_set(
        taxi_grocery_discounts,
        {
            'name': 'bin_set3',
            'time': {
                'start': '2020-01-01T00:00:01',
                'end': '2020-01-01T00:00:03',
            },
            'bins': [1],
        },
    )
    initial_order = {'bin_set_names': ['bin_set1', 'bin_set2', 'bin_set3']}
    await common.set_bin_sets_priority(taxi_grocery_discounts, initial_order)

    await _post_bin_sets_priority_check(
        taxi_grocery_discounts, data, expected_body, expected_status_code,
    )
    await _get_bin_sets_priority(
        taxi_grocery_discounts,
        {
            'active_bin_sets': initial_order['bin_set_names'],
            'old_bin_sets': ['old_bin_set'],
        },
        200,
    )
