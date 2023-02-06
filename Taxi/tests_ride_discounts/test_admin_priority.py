import datetime
from typing import List
from typing import Optional

import pytest

from tests_ride_discounts import common

PRIORITY_CHECK_URL = '/v1/admin/priority/check/'


def _multiple_groups_supported(prioritized_entity_type: str) -> bool:
    return False


def _entities_creation_required(prioritized_entity_type: str) -> bool:
    return prioritized_entity_type == 'bin_set'


async def _get_priority(
        taxi_ride_discounts,
        prioritized_entity_type: str,
        expected_body: Optional[dict],
        expected_status_code: int = 200,
) -> None:
    response = await taxi_ride_discounts.get(
        common.PRIORITY_URL,
        params={'prioritized_entity_type': prioritized_entity_type},
        headers=common.get_headers(),
    )
    assert response.status_code == expected_status_code
    if expected_body is not None:
        assert response.json() == expected_body


async def _post_priority_check(
        taxi_ride_discounts,
        request_body: dict,
        expected_body: Optional[dict],
        expected_status_code: int = 200,
) -> None:
    response = await taxi_ride_discounts.post(
        PRIORITY_CHECK_URL, request_body, headers=common.get_headers(),
    )
    assert response.status_code == expected_status_code
    if expected_body is not None:
        assert response.json() == expected_body


@pytest.mark.parametrize(
    'prioritized_entity_type',
    (
        pytest.param('unsupported_entity_type', id='unsupported_entity_type'),
        pytest.param('bin_set', id='bin_set'),
        pytest.param('class', id='class'),
        pytest.param('experiment', id='experiment'),
    ),
)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_priority_get(
        client,
        mocked_time,
        prioritized_entity_type: str,
        add_prioritized_entity,
):
    expected_body: dict = {
        'prioritized_entity_type': prioritized_entity_type,
        'priority_groups': [
            {
                'name': 'default',
                'entities_names': ['experimental', 'prioritized_entity'],
            },
        ],
    }
    expected_status_code: int = 200
    if _entities_creation_required(prioritized_entity_type):
        expected_body['priority_groups'][0]['entities_names'] = [
            'experimental',
        ]
        await add_prioritized_entity(
            {
                'name': 'old_bin_set',
                'data': {
                    'active_period': {
                        'start': '2019-01-01T00:00:01',
                        'end': '2019-01-01T00:00:03',
                    },
                    'prioritized_entity_type': prioritized_entity_type,
                    'bins': ['600000'],
                },
            },
        )
        await add_prioritized_entity(
            {
                'name': 'experimental',
                'data': {
                    'prioritized_entity_type': prioritized_entity_type,
                    'bins': ['600000'],
                    'active_period': {
                        'start': '2020-01-01T00:00:01',
                        'end': '2020-01-01T00:00:03',
                    },
                },
            },
        )
    elif _multiple_groups_supported(prioritized_entity_type):
        await common.set_priority(
            client,
            {
                'prioritized_entity_type': prioritized_entity_type,
                'priority_groups': [
                    {
                        'name': 'group',
                        'entities_names': [
                            'experimental',
                            'old_prioritized_entity',
                        ],
                    },
                ],
            },
        )
        mocked_time.set(mocked_time.now() + datetime.timedelta(seconds=1))
        await common.set_priority(
            client,
            {
                'prioritized_entity_type': prioritized_entity_type,
                'priority_groups': [
                    {
                        'name': 'group',
                        'entities_names': [
                            'experimental',
                            'prioritized_entity',
                        ],
                    },
                ],
            },
        )
        expected_body['priority_groups'][0]['name'] = 'group'
    elif prioritized_entity_type != 'unsupported_entity_type':
        await common.set_priority(
            client,
            {
                'prioritized_entity_type': prioritized_entity_type,
                'priority_groups': [
                    {
                        'name': 'default',
                        'entities_names': [
                            'experimental',
                            'old_prioritized_entity',
                        ],
                    },
                ],
            },
        )
        mocked_time.set(mocked_time.now() + datetime.timedelta(seconds=1))
        await common.set_priority(
            client,
            {
                'prioritized_entity_type': prioritized_entity_type,
                'priority_groups': [
                    {
                        'name': 'default',
                        'entities_names': [
                            'experimental',
                            'prioritized_entity',
                        ],
                    },
                ],
            },
        )
    else:
        expected_body = {
            'code': 'Validation error',
            'message': (
                'Operation not supported for '
                'prioritized_entity_type '
                f'{prioritized_entity_type}.'
            ),
        }
        expected_status_code = 400

    await _get_priority(
        client, prioritized_entity_type, expected_body, expected_status_code,
    )


@pytest.mark.parametrize(
    'handler',
    (
        pytest.param(common.PRIORITY_URL, id='priority'),
        pytest.param(PRIORITY_CHECK_URL, id='check_priority'),
    ),
)
@pytest.mark.parametrize(
    'prioritized_entity_type, expected_body',
    (
        pytest.param(
            'unsupported_entity_type',
            {
                'code': 'Validation error',
                'message': (
                    'Operation not supported for '
                    'prioritized_entity_type '
                    'unsupported_entity_type.'
                ),
            },
            id='unsupported_entity_type',
        ),
        pytest.param(
            'bin_set',
            {
                'code': 'Validation error',
                'message': (
                    'Not all active bin sets provided. Check all bin sets.'
                ),
            },
            id='bin_set',
        ),
        pytest.param('class', None, id='class'),
        pytest.param('experiment', None, id='experiment'),
    ),
)
@pytest.mark.parametrize(
    'request_body',
    (
        pytest.param(
            {
                'priority_groups': [
                    {'name': 'default', 'entities_names': ['experimental']},
                ],
            },
            id='default_group',
        ),
    ),
)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_priority_entity_creation_required(
        taxi_ride_discounts,
        mocked_time,
        handler: str,
        prioritized_entity_type: str,
        expected_body: Optional[dict],
        request_body: dict,
):
    if _entities_creation_required(prioritized_entity_type):
        expected_status_code = 400
    elif prioritized_entity_type == 'unsupported_entity_type':
        expected_status_code = 400
    else:
        expected_status_code = 200

    request_body['prioritized_entity_type'] = prioritized_entity_type

    if handler == PRIORITY_CHECK_URL:
        if expected_status_code == 200:
            expected_body = {
                'change_doc_id': f'{prioritized_entity_type}-priority',
                'data': request_body,
                'diff': {
                    'current': {
                        'prioritized_entity_type': prioritized_entity_type,
                        'priority_groups': [],
                    },
                    'new': request_body,
                },
            }
            if not _multiple_groups_supported(prioritized_entity_type):
                expected_body['diff']['current']['priority_groups'].append(
                    {'entities_names': [], 'name': 'default'},
                )
        await _post_priority_check(
            taxi_ride_discounts,
            request_body,
            expected_body,
            expected_status_code,
        )
    else:
        await common.set_priority(
            taxi_ride_discounts,
            request_body,
            expected_body,
            expected_status_code,
        )


@pytest.mark.parametrize(
    'handler',
    (
        pytest.param(common.PRIORITY_URL, id='priority'),
        pytest.param(PRIORITY_CHECK_URL, id='check_priority'),
    ),
)
@pytest.mark.parametrize(
    'prioritized_entity_type, prioritized_entities',
    (
        pytest.param(
            'bin_set',
            [
                {
                    'name': 'experimental',
                    'data': {
                        'prioritized_entity_type': 'bin_set',
                        'bins': ['222100'],
                        'active_period': {
                            'start': '2020-01-01T00:00:01',
                            'end': '2020-01-01T00:00:03',
                        },
                    },
                },
            ],
            id='bin_set',
        ),
        pytest.param('class', [], id='class'),
        pytest.param('experiment', [], id='experiment'),
    ),
)
@pytest.mark.parametrize(
    'request_body',
    (
        pytest.param({'priority_groups': []}, id='empty_groups'),
        pytest.param(
            {
                'priority_groups': [
                    {'name': 'default', 'entities_names': ['experimental']},
                ],
            },
            id='default_group',
        ),
        pytest.param(
            {
                'priority_groups': [
                    {'name': 'group', 'entities_names': ['experimental']},
                ],
            },
            id='custom_group',
        ),
        pytest.param(
            {
                'priority_groups': [
                    {'name': 'default', 'entities_names': ['experimental']},
                    {'name': 'group', 'entities_names': ['experimental']},
                ],
            },
            id='multiple_groups_with_default',
        ),
        pytest.param(
            {
                'priority_groups': [
                    {'name': 'group1', 'entities_names': ['experimental']},
                    {'name': 'group2', 'entities_names': ['experimental']},
                ],
            },
            id='multiple_groups',
        ),
    ),
)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_priority_groups_support(
        client,
        mocked_time,
        handler: str,
        prioritized_entity_type: str,
        prioritized_entities: List[dict],
        request_body: dict,
        add_prioritized_entity,
):
    entities_names: List[str] = []
    for prioritized_entity in prioritized_entities:
        await add_prioritized_entity(prioritized_entity)
        entities_names.append(prioritized_entity['name'])

    request_body['prioritized_entity_type'] = prioritized_entity_type

    expected_body: Optional[dict] = request_body
    expected_status_code = 200
    support_multiple_groups = _multiple_groups_supported(
        prioritized_entity_type,
    )
    if not support_multiple_groups:
        groups_number = len(request_body['priority_groups'])
        if groups_number != 1:
            expected_body = {
                'code': 'Validation error',
                'message': (
                    f'Exactly 1 group expected, {groups_number} received'
                ),
            }
            expected_status_code = 400
        elif request_body['priority_groups'][0]['name'] != 'default':
            group_name = request_body['priority_groups'][0]['name']
            expected_body = {
                'code': 'Validation error',
                'message': (
                    'Unexpected priority_group name '
                    f'{group_name}, \'default\' expected'
                ),
            }
            expected_status_code = 400

    if handler == PRIORITY_CHECK_URL:
        if expected_status_code == 200:
            expected_body = {
                'change_doc_id': f'{prioritized_entity_type}-priority',
                'data': expected_body,
                'diff': {
                    'current': {
                        'prioritized_entity_type': prioritized_entity_type,
                        'priority_groups': [],
                    },
                    'new': expected_body,
                },
            }
            if not support_multiple_groups:
                expected_body['diff']['current']['priority_groups'].append(
                    {'entities_names': entities_names, 'name': 'default'},
                )
        await _post_priority_check(
            client, request_body, expected_body, expected_status_code,
        )
    else:
        await common.set_priority(
            client, request_body, expected_body, expected_status_code,
        )


@pytest.mark.parametrize(
    'handler',
    (
        pytest.param(common.PRIORITY_URL, id='priority'),
        pytest.param(PRIORITY_CHECK_URL, id='check_priority'),
    ),
)
@pytest.mark.parametrize(
    'prioritized_entity_type',
    (
        pytest.param('class', id='class'),
        pytest.param('experiment', id='experiment'),
    ),
)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_priority_single_group_simple_entity_creation_not_required(
        taxi_ride_discounts,
        mocked_time,
        handler: str,
        prioritized_entity_type: str,
):
    async def _check(
            taxi_ride_discounts,
            mocked_time,
            handler: str,
            prioritized_entity_type: str,
            entities_names: List[str],
            expected_status_code: int = 200,
            old_entities_names: Optional[List[str]] = None,
    ):
        priority: dict = {
            'prioritized_entity_type': prioritized_entity_type,
            'priority_groups': [
                {'name': 'default', 'entities_names': entities_names},
            ],
        }
        mocked_time.set(mocked_time.now() + datetime.timedelta(seconds=1))
        if handler == PRIORITY_CHECK_URL:
            expected_body: Optional[dict] = None
            initial_priority_body = {
                'prioritized_entity_type': prioritized_entity_type,
                'priority_groups': [{'name': 'default', 'entities_names': []}],
            }
            if expected_status_code == 200:
                expected_body = {
                    'change_doc_id': f'{prioritized_entity_type}-priority',
                    'data': priority,
                    'diff': {
                        'current': initial_priority_body,
                        'new': priority,
                    },
                }

            await _post_priority_check(
                taxi_ride_discounts,
                priority,
                expected_body,
                expected_status_code,
            )
            await _get_priority(
                taxi_ride_discounts,
                prioritized_entity_type,
                initial_priority_body,
            )
        else:
            await common.set_priority(
                taxi_ride_discounts, priority, None, expected_status_code,
            )
            if expected_status_code != 200:
                priority['priority_groups'][0][
                    'entities_names'
                ] = old_entities_names
            await _get_priority(
                taxi_ride_discounts, prioritized_entity_type, priority,
            )

    assert not _multiple_groups_supported(prioritized_entity_type)
    assert not _entities_creation_required(prioritized_entity_type)

    await _check(
        taxi_ride_discounts, mocked_time, handler, prioritized_entity_type, [],
    )

    await _check(
        taxi_ride_discounts,
        mocked_time,
        handler,
        prioritized_entity_type,
        ['experimental', 'experimental_1'],
    )

    await _check(
        taxi_ride_discounts, mocked_time, handler, prioritized_entity_type, [],
    )

    entities_names = ['experimental', 'experimental_1', 'experimental_2']
    await _check(
        taxi_ride_discounts,
        mocked_time,
        handler,
        prioritized_entity_type,
        entities_names,
    )

    await _check(
        taxi_ride_discounts,
        mocked_time,
        handler,
        prioritized_entity_type,
        [''],
        400,
        entities_names,
    )

    await _check(
        taxi_ride_discounts, mocked_time, handler, prioritized_entity_type, [],
    )


@pytest.mark.parametrize(
    'handler',
    (
        pytest.param(common.PRIORITY_URL, id='priority'),
        pytest.param(PRIORITY_CHECK_URL, id='check_priority'),
    ),
)
@pytest.mark.parametrize(
    'prioritized_entity_type, prioritized_entities, initial_priority',
    (
        pytest.param(
            'bin_set',
            [
                {
                    'name': 'old_bin_set',
                    'data': {
                        'prioritized_entity_type': 'bin_set',
                        'bins': ['222100'],
                        'active_period': {
                            'start': '2019-01-01T00:00:01',
                            'end': '2019-01-01T00:00:03',
                        },
                    },
                },
                {
                    'name': 'bin_set1',
                    'data': {
                        'prioritized_entity_type': 'bin_set',
                        'bins': ['222100'],
                        'active_period': {
                            'start': '2020-01-01T00:00:01',
                            'end': '2020-01-01T00:00:03',
                        },
                    },
                },
                {
                    'name': 'bin_set2',
                    'data': {
                        'prioritized_entity_type': 'bin_set',
                        'bins': ['222100'],
                        'active_period': {
                            'start': '2020-01-01T00:00:01',
                            'end': '2020-01-01T00:00:03',
                        },
                    },
                },
                {
                    'name': 'bin_set3',
                    'data': {
                        'prioritized_entity_type': 'bin_set',
                        'bins': ['222100'],
                        'active_period': {
                            'start': '2020-01-01T00:00:01',
                            'end': '2020-01-01T00:00:03',
                        },
                    },
                },
            ],
            ['bin_set1', 'bin_set2', 'bin_set3'],
            id='bin_set',
        ),
    ),
)
@pytest.mark.parametrize(
    'priority, expected_body, expected_status_code',
    (
        pytest.param(
            ['bin_set1', 'bin_set2', 'bin_set3'],
            {
                'prioritized_entity_type': 'bin_set',
                'priority_groups': [
                    {
                        'name': 'default',
                        'entities_names': ['bin_set1', 'bin_set2', 'bin_set3'],
                    },
                ],
            },
            200,
            id='all_active',
        ),
        pytest.param(
            [],
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
            ['bin_set1'],
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
            ['bin_set1', 'bin_set2', 'bin_set3', 'bin_set4'],
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
            ['bin_set1', 'bin_set3', 'bin_set3'],
            {
                'code': 'Validation error',
                'message': 'Provided duplicate bin sets to save: bin_set3',
            },
            400,
            id='duplicate_bin_set',
        ),
        pytest.param(
            ['bin_set1', 'bin_set2', 'old_bin_set'],
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
            ['bin_set1', 'bin_set2', 'bin_set4'],
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
            ['bin_set3', 'bin_set2', 'bin_set1'],
            {
                'prioritized_entity_type': 'bin_set',
                'priority_groups': [
                    {
                        'name': 'default',
                        'entities_names': ['bin_set3', 'bin_set2', 'bin_set1'],
                    },
                ],
            },
            200,
            id='all_active_reverse',
        ),
    ),
)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_priority_single_group_complex_entity_creation_required(
        client,
        handler: str,
        prioritized_entity_type: str,
        prioritized_entities: List[dict],
        initial_priority: List[str],
        priority: List[str],
        expected_body: dict,
        expected_status_code: int,
        add_prioritized_entity,
):
    assert not _multiple_groups_supported(prioritized_entity_type)
    assert _entities_creation_required(prioritized_entity_type)

    for prioritized_entity in prioritized_entities:
        await add_prioritized_entity(prioritized_entity)

    initial_priority_body = {
        'prioritized_entity_type': prioritized_entity_type,
        'priority_groups': [
            {'name': 'default', 'entities_names': initial_priority},
        ],
    }
    await common.set_priority(client, initial_priority_body)
    request_body = {
        'prioritized_entity_type': prioritized_entity_type,
        'priority_groups': [{'name': 'default', 'entities_names': priority}],
    }
    if handler == PRIORITY_CHECK_URL:
        if expected_status_code == 200:
            expected_body = {
                'change_doc_id': f'{prioritized_entity_type}-priority',
                'data': expected_body,
                'diff': {
                    'current': initial_priority_body,
                    'new': expected_body,
                },
            }

        await _post_priority_check(
            client, request_body, expected_body, expected_status_code,
        )
        await _get_priority(
            client, prioritized_entity_type, initial_priority_body,
        )
    else:
        await common.set_priority(
            client, request_body, expected_body, expected_status_code,
        )
        await _get_priority(
            client,
            prioritized_entity_type,
            request_body
            if expected_status_code == 200
            else initial_priority_body,
        )
