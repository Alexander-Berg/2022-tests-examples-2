from typing import List
from typing import Optional

import pytest

from tests_eats_discounts import common

BIN_SETS_PRIORITY_CHECK_URL = '/v1/admin/bin-sets-priority/check'


async def _get_bin_sets_priority(
        taxi_eats_discounts,
        expected_body: Optional[dict],
        expected_status_code: int = 200,
) -> None:
    response = await taxi_eats_discounts.get(
        common.BIN_SETS_PRIORITY_URL, headers=common.get_headers(),
    )
    assert response.status_code == expected_status_code
    if expected_body is not None:
        assert response.json() == expected_body


async def _post_bin_sets_priority_check(
        taxi_eats_discounts,
        request: dict,
        expected_body: Optional[dict],
        expected_status_code: int = 200,
) -> None:
    response = await taxi_eats_discounts.post(
        BIN_SETS_PRIORITY_CHECK_URL, request, headers=common.get_headers(),
    )
    assert response.status_code == expected_status_code
    if expected_body is not None:
        assert response.json() == expected_body


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
        taxi_eats_discounts, old_added: bool, active_added: bool,
):
    if old_added:
        await common.add_bin_set(
            taxi_eats_discounts,
            {
                'name': 'old_bin_set',
                'active_period': {
                    'start': '2019-01-01T00:00:01',
                    'end': '2019-01-01T00:00:03',
                },
                'bins': ['1'],
            },
        )
    if active_added:
        await common.add_bin_set(
            taxi_eats_discounts,
            {
                'name': 'bin_set',
                'active_period': {
                    'start': '2020-01-01T00:00:01',
                    'end': '2020-01-01T00:00:03',
                },
                'bins': ['1'],
            },
        )

    active_bin_sets: List[str] = []
    if active_added:
        active_bin_sets.append('bin_set')

    old_bin_sets = []
    if old_added:
        old_bin_sets.append('old_bin_set')
    await _get_bin_sets_priority(
        taxi_eats_discounts,
        {'active_bin_sets': active_bin_sets, 'old_bin_sets': old_bin_sets},
        200,
    )


@pytest.mark.parametrize(
    'data, expected_body, expected_status_code',
    (
        pytest.param(
            {'bin_sets_names': ['bin_set1', 'bin_set2', 'bin_set3']},
            {'bin_sets_names': ['bin_set1', 'bin_set2', 'bin_set3']},
            200,
            id='all_active',
        ),
        pytest.param(
            {'bin_sets_names': []},
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
            {'bin_sets_names': ['bin_set1']},
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
                'bin_sets_names': [
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
            {'bin_sets_names': ['bin_set1', 'bin_set3', 'bin_set3']},
            {
                'code': 'Validation error',
                'message': 'Provided duplicate bin sets to save: bin_set3',
            },
            400,
            id='duplicate_bin_set',
        ),
        pytest.param(
            {'bin_sets_names': ['bin_set1', 'bin_set2', 'old_bin_set']},
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
            {'bin_sets_names': ['bin_set1', 'bin_set2', 'bin_set4']},
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
            {'bin_sets_names': ['bin_set3', 'bin_set2', 'bin_set1']},
            {'bin_sets_names': ['bin_set3', 'bin_set2', 'bin_set1']},
            200,
            id='all_active_reverse',
        ),
    ),
)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_bin_sets_priority(
        taxi_eats_discounts,
        data: dict,
        expected_body: Optional[dict],
        expected_status_code: int,
):
    await common.add_bin_set(
        taxi_eats_discounts,
        {
            'name': 'old_bin_set',
            'active_period': {
                'start': '2019-01-01T00:00:01',
                'end': '2019-01-01T00:00:03',
            },
            'bins': ['1'],
        },
    )

    await common.add_bin_set(
        taxi_eats_discounts,
        {
            'name': 'bin_set1',
            'active_period': {
                'start': '2020-01-01T00:00:01',
                'end': '2020-01-01T00:00:03',
            },
            'bins': ['1'],
        },
    )

    await common.add_bin_set(
        taxi_eats_discounts,
        {
            'name': 'bin_set2',
            'active_period': {
                'start': '2020-01-01T00:00:01',
                'end': '2020-01-01T00:00:03',
            },
            'bins': ['1'],
        },
    )

    await common.add_bin_set(
        taxi_eats_discounts,
        {
            'name': 'bin_set3',
            'active_period': {
                'start': '2020-01-01T00:00:01',
                'end': '2020-01-01T00:00:03',
            },
            'bins': ['1'],
        },
    )
    initial_order = {'bin_sets_names': ['bin_set1', 'bin_set2', 'bin_set3']}
    await common.set_bin_sets_priority(taxi_eats_discounts, initial_order)

    await common.set_bin_sets_priority(
        taxi_eats_discounts, data, expected_body, expected_status_code,
    )
    order = (
        expected_body['bin_sets_names']
        if expected_status_code == 200 and expected_body is not None
        else initial_order['bin_sets_names']
    )

    await _get_bin_sets_priority(
        taxi_eats_discounts,
        {'active_bin_sets': order, 'old_bin_sets': ['old_bin_set']},
        200,
    )


@pytest.mark.parametrize(
    'data, expected_body, expected_status_code',
    (
        pytest.param(
            {'bin_sets_names': ['bin_set1', 'bin_set2', 'bin_set3']},
            {
                'change_doc_id': 'bin-sets-priorities',
                'data': {
                    'bin_sets_names': ['bin_set1', 'bin_set2', 'bin_set3'],
                },
                'diff': {
                    'current': {
                        'bin_sets_names': ['bin_set1', 'bin_set2', 'bin_set3'],
                    },
                    'new': {
                        'bin_sets_names': ['bin_set1', 'bin_set2', 'bin_set3'],
                    },
                },
            },
            200,
            id='all_active',
        ),
        pytest.param(
            {'bin_sets_names': []},
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
            {'bin_sets_names': ['bin_set1']},
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
                'bin_sets_names': [
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
            {'bin_sets_names': ['bin_set1', 'bin_set3', 'bin_set3']},
            {
                'code': 'Validation error',
                'message': 'Provided duplicate bin sets to save: bin_set3',
            },
            400,
            id='duplicate_bin_set',
        ),
        pytest.param(
            {'bin_sets_names': ['bin_set1', 'bin_set2', 'old_bin_set']},
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
            {'bin_sets_names': ['bin_set1', 'bin_set2', 'bin_set4']},
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
            {'bin_sets_names': ['bin_set3', 'bin_set2', 'bin_set1']},
            {
                'change_doc_id': 'bin-sets-priorities',
                'data': {
                    'bin_sets_names': ['bin_set3', 'bin_set2', 'bin_set1'],
                },
                'diff': {
                    'current': {
                        'bin_sets_names': ['bin_set1', 'bin_set2', 'bin_set3'],
                    },
                    'new': {
                        'bin_sets_names': ['bin_set3', 'bin_set2', 'bin_set1'],
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
        taxi_eats_discounts,
        data: dict,
        expected_body: Optional[dict],
        expected_status_code: int,
):
    await common.add_bin_set(
        taxi_eats_discounts,
        {
            'name': 'old_bin_set',
            'active_period': {
                'start': '2019-01-01T00:00:01',
                'end': '2019-01-01T00:00:03',
            },
            'bins': ['1'],
        },
    )

    await common.add_bin_set(
        taxi_eats_discounts,
        {
            'name': 'bin_set1',
            'active_period': {
                'start': '2020-01-01T00:00:01',
                'end': '2020-01-01T00:00:03',
            },
            'bins': ['1'],
        },
    )

    await common.add_bin_set(
        taxi_eats_discounts,
        {
            'name': 'bin_set2',
            'active_period': {
                'start': '2020-01-01T00:00:01',
                'end': '2020-01-01T00:00:03',
            },
            'bins': ['1'],
        },
    )

    await common.add_bin_set(
        taxi_eats_discounts,
        {
            'name': 'bin_set3',
            'active_period': {
                'start': '2020-01-01T00:00:01',
                'end': '2020-01-01T00:00:03',
            },
            'bins': ['1'],
        },
    )
    initial_order = {'bin_sets_names': ['bin_set1', 'bin_set2', 'bin_set3']}
    await common.set_bin_sets_priority(taxi_eats_discounts, initial_order)

    await _post_bin_sets_priority_check(
        taxi_eats_discounts, data, expected_body, expected_status_code,
    )
    await _get_bin_sets_priority(
        taxi_eats_discounts,
        {
            'active_bin_sets': initial_order['bin_sets_names'],
            'old_bin_sets': ['old_bin_set'],
        },
        200,
    )
