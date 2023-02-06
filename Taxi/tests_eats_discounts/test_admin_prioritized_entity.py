from typing import Optional

import pytest

from tests_eats_discounts import common


async def _get_prioritized_entity(
        taxi_eats_discounts,
        prioritized_entity_type: str,
        prioritized_entity_name: str,
        expected_body: Optional[dict],
        expected_status_code: int = 200,
) -> None:
    response = await taxi_eats_discounts.get(
        common.PRIORITIZED_ENTITY_URL,
        params={
            'name': prioritized_entity_name,
            'prioritized_entity_type': prioritized_entity_type,
        },
        headers=common.get_headers(),
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
        pytest.param('tag', id='tag'),
        pytest.param('experiment', id='experiment'),
    ),
)
@pytest.mark.parametrize(
    'prioritized_entity_name',
    (
        pytest.param(
            'missing_prioritized_entity', id='missing_prioritized_entity',
        ),
        pytest.param('', id='invalid_prioritized_entity'),
        pytest.param('prioritized_entity', id='prioritized_entity'),
    ),
)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_prioritized_entity_get(
        taxi_eats_discounts,
        prioritized_entity_type: str,
        prioritized_entity_name: str,
        add_prioritized_entity,
):
    request_body = {
        'name': 'prioritized_entity',
        'data': {
            'prioritized_entity_type': prioritized_entity_type,
            'bins': ['1', '2'],
            'active_period': {
                'start': '2020-01-01T00:00:01',
                'end': '2020-01-01T00:00:02',
            },
        },
    }

    expected_status_code: int = 0
    expected_body: Optional[dict] = None
    if prioritized_entity_type == 'bin_set':
        await add_prioritized_entity(request_body)
        if prioritized_entity_name == request_body['name']:
            expected_status_code = 200
        elif prioritized_entity_name == 'missing_prioritized_entity':
            expected_status_code = 404
        else:
            expected_status_code = 400
    else:
        expected_status_code = 400

    if expected_status_code == 200:
        expected_body = request_body
    elif expected_status_code == 404:
        expected_body = {
            'code': 'Not found',
            'message': (
                'Couldn\'t find prioritized_entity named '
                f'{prioritized_entity_name}.'
            ),
        }
    elif expected_status_code == 400:
        if prioritized_entity_name:
            expected_body = {
                'code': 'Validation error',
                'message': (
                    'Operation not supported for '
                    'prioritized_entity_type '
                    f'{prioritized_entity_type}.'
                ),
            }

    await _get_prioritized_entity(
        taxi_eats_discounts,
        prioritized_entity_type,
        prioritized_entity_name,
        expected_body,
        expected_status_code,
    )


@pytest.mark.parametrize(
    'handler',
    (pytest.param(common.PRIORITIZED_ENTITY_URL, id='prioritized_entity'),),
)
@pytest.mark.parametrize(
    'request_body, expected_status_code, expected_body',
    (
        pytest.param(
            {
                'name': 'new_bin_set',
                'data': {
                    'prioritized_entity_type': 'bin_set',
                    'bins': ['1'],
                    'active_period': {
                        'start': '2020-01-01T00:00:01',
                        'end': '2020-01-01T00:00:02',
                    },
                },
            },
            200,
            {
                'name': 'new_bin_set',
                'data': {
                    'prioritized_entity_type': 'bin_set',
                    'bins': ['1'],
                    'active_period': {
                        'start': '2020-01-01T00:00:01',
                        'end': '2020-01-01T00:00:02',
                    },
                },
            },
            id='insert_new_bin_set',
        ),
        pytest.param(
            {
                'name': 'new_bin_set',
                'data': {
                    'prioritized_entity_type': 'bin_set',
                    'bins': [],
                    'active_period': {
                        'start': '2020-01-01T00:00:01',
                        'end': '2020-01-01T00:00:02',
                    },
                },
            },
            400,
            None,
            id='empty_bins',
        ),
        pytest.param(
            {
                'name': 'new_bin_set',
                'data': {
                    'prioritized_entity_type': 'bin_set',
                    'bins': ['1'],
                    'active_period': {
                        'start': '2020-01-01T00:00:02',
                        'end': '2020-01-01T00:00:01',
                    },
                },
            },
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Start 2020-01-01T00:00:02 cannot be more or '
                    'equal than end 2020-01-01T00:00:01.'
                ),
            },
            id='start_before_end',
        ),
        pytest.param(
            {
                'name': 'new_bin_set',
                'data': {
                    'prioritized_entity_type': 'bin_set',
                    'bins': ['1'],
                    'active_period': {
                        'start': '2020-01-01T00:00:01',
                        'end': '2020-01-01T00:00:01',
                    },
                },
            },
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Start 2020-01-01T00:00:01 cannot be more or '
                    'equal than end 2020-01-01T00:00:01.'
                ),
            },
            id='start_equal_end',
        ),
        pytest.param(
            {
                'name': 'bin_set',
                'data': {
                    'prioritized_entity_type': 'bin_set',
                    'bins': ['1'],
                    'active_period': {
                        'start': '2020-01-01T00:00:01',
                        'end': '2020-01-01T00:00:04',
                    },
                },
            },
            200,
            {
                'name': 'bin_set',
                'data': {
                    'prioritized_entity_type': 'bin_set',
                    'bins': ['1'],
                    'active_period': {
                        'start': '2020-01-01T00:00:01',
                        'end': '2020-01-01T00:00:04',
                    },
                },
            },
            id='increase_end_time',
        ),
        pytest.param(
            {
                'name': 'bin_set',
                'data': {
                    'prioritized_entity_type': 'bin_set',
                    'bins': ['1'],
                    'active_period': {
                        'start': '2020-01-01T00:00:01',
                        'end': '2020-01-01T00:00:02',
                    },
                },
            },
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Couldn\'t update bin set bin_set. Bin set time '
                    'could only be extended!'
                ),
            },
            id='decrease_end_time',
        ),
        pytest.param(
            {
                'name': 'bin_set',
                'data': {
                    'prioritized_entity_type': 'bin_set',
                    'bins': ['1'],
                    'active_period': {
                        'start': '2020-01-01T00:00:02',
                        'end': '2020-01-01T00:00:03',
                    },
                },
            },
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Couldn\'t update bin set bin_set. From_ts cannot '
                    'be changed!'
                ),
            },
            id='increase_start_time',
        ),
        pytest.param(
            {
                'name': 'bin_set',
                'data': {
                    'prioritized_entity_type': 'bin_set',
                    'bins': ['1'],
                    'active_period': {
                        'start': '2020-01-01T00:00:00',
                        'end': '2020-01-01T00:00:03',
                    },
                },
            },
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Couldn\'t update bin set bin_set. From_ts cannot '
                    'be changed!'
                ),
            },
            id='decrease_start_time',
        ),
        pytest.param(
            {
                'name': 'old_bin_set',
                'data': {
                    'prioritized_entity_type': 'bin_set',
                    'bins': ['1'],
                    'active_period': {
                        'start': '2020-01-01T00:00:01',
                        'end': '2020-01-01T00:00:04',
                    },
                },
            },
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Couldn\'t update bin set old_bin_set. Bin set is '
                    'inactive. Please create a new one. Only active bin '
                    'set\'s time could be extend!'
                ),
            },
            id='increase_old_bin_set_end_time',
        ),
        pytest.param(
            {
                'name': 'bin_set',
                'data': {
                    'prioritized_entity_type': 'bin_set',
                    'bins': ['1', '2'],
                    'active_period': {
                        'start': '2020-01-01T00:00:01',
                        'end': '2020-01-01T00:00:03',
                    },
                },
            },
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Couldn\'t update bin set bin_set. Bins cannot be changed!'
                ),
            },
            id='change_bins',
        ),
        pytest.param(
            {
                'name': 'new_bin_set',
                'data': {
                    'prioritized_entity_type': 'class',
                    'active_period': {
                        'start': '2020-01-01T00:00:01',
                        'end': '2020-01-01T00:00:02',
                    },
                },
            },
            400,
            None,
            id='wrong_data_type',
        ),
    ),
)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_prioritized_entity_bin_set(
        client,
        handler: str,
        request_body: dict,
        expected_status_code: int,
        expected_body: Optional[dict],
        add_prioritized_entity,
):
    prioritized_entity_type = 'bin_set'
    post_old_bin_set_request = {
        'name': 'old_bin_set',
        'data': {
            'prioritized_entity_type': 'bin_set',
            'bins': ['1'],
            'active_period': {
                'start': '2019-01-01T00:00:01',
                'end': '2019-01-01T00:00:03',
            },
        },
    }
    await add_prioritized_entity(post_old_bin_set_request)

    post_bin_set_request = {
        'name': 'bin_set',
        'data': {
            'prioritized_entity_type': 'bin_set',
            'bins': ['1'],
            'active_period': {
                'start': '2020-01-01T00:00:01',
                'end': '2020-01-01T00:00:03',
            },
        },
    }

    await add_prioritized_entity(post_bin_set_request)

    prioritized_entity_name = request_body['name']

    await add_prioritized_entity(
        request_body, expected_body, expected_status_code,
    )

    if expected_status_code == 200:
        await _get_prioritized_entity(
            client,
            prioritized_entity_type,
            prioritized_entity_name,
            expected_body,
            expected_status_code,
        )
    elif prioritized_entity_name in {'bin_set', 'old_bin_set'}:
        await _get_prioritized_entity(
            client,
            prioritized_entity_type,
            prioritized_entity_name,
            post_bin_set_request
            if prioritized_entity_name == 'bin_set'
            else post_old_bin_set_request,
            200,
        )
    else:
        await _get_prioritized_entity(
            client,
            prioritized_entity_type,
            prioritized_entity_name,
            {
                'code': 'Not found',
                'message': (
                    'Couldn\'t find prioritized_entity named '
                    f'{prioritized_entity_name}.'
                ),
            },
            404,
        )
