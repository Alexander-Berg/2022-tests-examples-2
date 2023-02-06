import http
import json
from typing import List
from typing import Optional

import pytest

from tests_grocery_discounts import common

BIN_SET_CHECK_URL = '/v3/admin/bin-set/check'


async def _get_bin_set(
        taxi_grocery_discounts,
        bin_set_name: str,
        expected_body: Optional[dict],
        expected_status_code: int = 200,
) -> None:
    response = await taxi_grocery_discounts.get(
        common.BIN_SET_URL,
        params={'bin_set_name': bin_set_name},
        headers=common.get_headers(),
    )
    assert response.status_code == expected_status_code
    if expected_body is not None:
        assert response.json() == expected_body


async def _post_bin_set_check(
        taxi_grocery_discounts,
        request: dict,
        expected_body: Optional[dict],
        expected_status_code: int = 200,
) -> None:
    response = await taxi_grocery_discounts.post(
        BIN_SET_CHECK_URL, request, headers=common.get_headers(),
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
            {
                'name': 'Тест',
                'bins': [123321, 221122],
                'time': {
                    'start': '2020-02-01T18:00:00',
                    'end': '2020-09-01T18:00:00',
                },
            },
            http.HTTPStatus.OK,
            {'change_doc_id': 'Тест'},
        ),
        (
            {
                'name': 'Любимое',
                'bins': [123321, 234432],
                'time': {
                    'start': '2020-07-11T05:00:00',
                    'end': '2020-07-20T18:00:00',
                },
            },
            http.HTTPStatus.OK,
            {
                'change_doc_id': 'Любимое',
                'diff': {
                    'current': {
                        'bins': [123321, 234432],
                        'name': 'Любимое',
                        'time': {
                            'end': '2020-07-18T10:00:00',
                            'start': '2020-07-11T05:00:00',
                        },
                    },
                },
            },
        ),
        (
            {
                'name': 'Любимое',
                'bins': [123321, 234432],
                'time': {
                    'start': '2020-07-11T05:00:00',
                    'end': '2020-07-16T18:00:00',
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'Validation error',
                'message': (
                    'Couldn\'t update bin set Любимое.'
                    ' Bin set time could only be extended!'
                ),
            },
        ),
        (
            {
                'name': 'Любимое',
                'bins': [111333, 234432],
                'time': {
                    'start': '2020-07-11T05:00:00',
                    'end': '2020-07-20T18:00:00',
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'Validation error',
                'message': (
                    'Couldn\'t update bin set Любимое.'
                    ' Bins cannot be changed!'
                ),
            },
        ),
        (
            {
                'name': 'Любимое',
                'bins': [123321, 234432],
                'time': {
                    'start': '2020-07-13T02:00:00',
                    'end': '2020-07-20T18:00:00',
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'Validation error',
                'message': (
                    'Couldn\'t update bin set Любимое.'
                    ' From_ts cannot be changed!'
                ),
            },
        ),
        (
            {
                'name': 'Прошла',
                'bins': [213321, 123333],
                'time': {
                    'start': '2020-06-11T05:00:00',
                    'end': '2020-07-20T18:00:00',
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'Validation error',
                'message': (
                    'Couldn\'t update bin set Прошла.'
                    ' Bin set is inactive. Please create'
                    ' a new one. Only active bin set\'s'
                    ' time could be extend!'
                ),
            },
        ),
    ),
)
@pytest.mark.parametrize('url', [common.BIN_SET_URL, BIN_SET_CHECK_URL])
@pytest.mark.config(
    **common.DEFAULT_CONFIGS,
    GROCERY_DISCOUNTS_TIME_ZONES={'bins': 'Europe/Moscow'},
)
async def test_create_bin_sets(
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
            diff = expected_content.setdefault('diff', {})
            diff['new'] = body
        else:
            expected_content = body

    assert response.status_code == expected_status_code, response.json()
    assert response.json() == expected_content

    if expected_status_code == http.HTTPStatus.OK:
        if 'check' not in url:
            response = await taxi_grocery_discounts.get(
                common.BIN_SET_URL,
                params={'bin_set_name': body['name']},
                headers=common.DEFAULT_DISCOUNTS_HEADERS,
            )
            assert (
                response.status_code == expected_status_code
            ), response.json()
            assert response.json() == expected_content


@pytest.mark.parametrize(
    'bin_set_name, expected_status_code, expected_body',
    (
        pytest.param(
            'missing_bin_set',
            500,
            {
                'code': 'Not found',
                'message': 'Couldn\'t find bin set named missing_bin_set.',
            },
            id='missing_bin_set',
        ),
        pytest.param('', 400, None, id='invalid_bin_set'),
        pytest.param(
            'bin_set',
            200,
            {
                'name': 'bin_set',
                'time': {
                    'start': '2020-01-01T00:00:01',
                    'end': '2020-01-01T00:00:02',
                },
                'bins': [1, 2],
            },
            id='invalid_bin_set',
        ),
    ),
)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_bin_set_get(
        taxi_grocery_discounts,
        bin_set_name: str,
        expected_status_code: int,
        expected_body: dict,
):
    post_request = {
        'name': 'bin_set',
        'time': {'start': '2020-01-01T00:00:01', 'end': '2020-01-01T00:00:02'},
        'bins': [1, 2],
    }
    await common.add_bin_set(taxi_grocery_discounts, post_request)

    await _get_bin_set(
        taxi_grocery_discounts,
        bin_set_name,
        expected_body,
        expected_status_code,
    )


@pytest.mark.parametrize(
    'bin_set_name, start, end, bins, expected_status_code, expected_body',
    (
        pytest.param(
            'new_bin_set',
            '2020-01-01T00:00:01',
            '2020-01-01T00:00:02',
            [1],
            200,
            {
                'name': 'new_bin_set',
                'time': {
                    'start': '2020-01-01T00:00:01',
                    'end': '2020-01-01T00:00:02',
                },
                'bins': [1],
            },
            id='insert_new_bin_set',
        ),
        pytest.param(
            'new_bin_set',
            '2020-01-01T00:00:01',
            '2020-01-01T00:00:02',
            [],
            400,
            None,
            id='empty_bins',
        ),
        pytest.param(
            'new_bin_set',
            '2020-01-01T00:00:02',
            '2020-01-01T00:00:01',
            [1],
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
            'new_bin_set',
            '2020-01-01T00:00:01',
            '2020-01-01T00:00:01',
            [1],
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
            'bin_set',
            '2020-01-01T00:00:01',
            '2020-01-01T00:00:04',
            [1],
            200,
            {
                'name': 'bin_set',
                'time': {
                    'start': '2020-01-01T00:00:01',
                    'end': '2020-01-01T00:00:04',
                },
                'bins': [1],
            },
            id='increase_end_time',
        ),
        pytest.param(
            'bin_set',
            '2020-01-01T00:00:01',
            '2020-01-01T00:00:02',
            [1],
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
            'bin_set',
            '2020-01-01T00:00:02',
            '2020-01-01T00:00:03',
            [1],
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
            'bin_set',
            '2020-01-01T00:00:00',
            '2020-01-01T00:00:03',
            [1],
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
            'bin_set',
            '2020-01-01T00:00:01',
            '2020-01-01T00:00:03',
            [1, 2],
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
            'old_bin_set',
            '2020-01-01T00:00:01',
            '2020-01-01T00:00:04',
            [1],
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
    ),
)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_bin_set(
        taxi_grocery_discounts,
        bin_set_name: str,
        start: str,
        end: str,
        bins: List[int],
        expected_status_code: int,
        expected_body: Optional[dict],
):
    post_old_bin_set_request = {
        'name': 'old_bin_set',
        'time': {'start': '2019-01-01T00:00:01', 'end': '2019-01-01T00:00:03'},
        'bins': [1],
    }
    await common.add_bin_set(taxi_grocery_discounts, post_old_bin_set_request)

    post_bin_set_request = {
        'name': 'bin_set',
        'time': {'start': '2020-01-01T00:00:01', 'end': '2020-01-01T00:00:03'},
        'bins': [1],
    }
    await common.add_bin_set(taxi_grocery_discounts, post_bin_set_request)

    post_request = {
        'name': bin_set_name,
        'time': {'start': start, 'end': end},
        'bins': bins,
    }
    await common.add_bin_set(
        taxi_grocery_discounts,
        post_request,
        expected_body,
        expected_status_code,
    )

    if expected_status_code == 200:
        await _get_bin_set(
            taxi_grocery_discounts,
            bin_set_name,
            expected_body,
            expected_status_code,
        )
    elif bin_set_name in {'bin_set', 'old_bin_set'}:
        await _get_bin_set(
            taxi_grocery_discounts,
            bin_set_name,
            post_bin_set_request
            if bin_set_name == 'bin_set'
            else post_old_bin_set_request,
            200,
        )
    else:
        await _get_bin_set(
            taxi_grocery_discounts,
            bin_set_name,
            {
                'code': 'Not found',
                'message': f'Couldn\'t find bin set named {bin_set_name}.',
            },
            500,
        )


@pytest.mark.parametrize(
    'bin_set_name, start, end, bins, expected_status_code, expected_body',
    (
        pytest.param(
            'new_bin_set',
            '2020-01-01T00:00:01',
            '2020-01-01T00:00:02',
            [1],
            200,
            {
                'change_doc_id': 'new_bin_set',
                'data': {
                    'name': 'new_bin_set',
                    'time': {
                        'start': '2020-01-01T00:00:01',
                        'end': '2020-01-01T00:00:02',
                    },
                    'bins': [1],
                },
                'diff': {
                    'new': {
                        'name': 'new_bin_set',
                        'time': {
                            'start': '2020-01-01T00:00:01',
                            'end': '2020-01-01T00:00:02',
                        },
                        'bins': [1],
                    },
                },
            },
            id='insert_new_bin_set',
        ),
        pytest.param(
            'new_bin_set',
            '2020-01-01T00:00:01',
            '2020-01-01T00:00:02',
            [],
            400,
            None,
            id='empty_bins',
        ),
        pytest.param(
            'new_bin_set',
            '2020-01-01T00:00:02',
            '2020-01-01T00:00:01',
            [1],
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
            'new_bin_set',
            '2020-01-01T00:00:01',
            '2020-01-01T00:00:01',
            [1],
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
            'bin_set',
            '2020-01-01T00:00:01',
            '2020-01-01T00:00:04',
            [1],
            200,
            {
                'change_doc_id': 'bin_set',
                'data': {
                    'name': 'bin_set',
                    'time': {
                        'start': '2020-01-01T00:00:01',
                        'end': '2020-01-01T00:00:04',
                    },
                    'bins': [1],
                },
                'diff': {
                    'current': {
                        'bins': [1],
                        'name': 'bin_set',
                        'time': {
                            'end': '2020-01-01T00:00:03',
                            'start': '2020-01-01T00:00:01',
                        },
                    },
                    'new': {
                        'bins': [1],
                        'name': 'bin_set',
                        'time': {
                            'end': '2020-01-01T00:00:04',
                            'start': '2020-01-01T00:00:01',
                        },
                    },
                },
            },
            id='increase_end_time',
        ),
        pytest.param(
            'bin_set',
            '2020-01-01T00:00:01',
            '2020-01-01T00:00:02',
            [1],
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
            'bin_set',
            '2020-01-01T00:00:02',
            '2020-01-01T00:00:03',
            [1],
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
            'bin_set',
            '2020-01-01T00:00:00',
            '2020-01-01T00:00:03',
            [1],
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
            'bin_set',
            '2020-01-01T00:00:01',
            '2020-01-01T00:00:03',
            [1, 2],
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
            'old_bin_set',
            '2020-01-01T00:00:01',
            '2020-01-01T00:00:04',
            [1],
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
    ),
)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_bin_set_check(
        taxi_grocery_discounts,
        bin_set_name: str,
        start: str,
        end: str,
        bins: List[int],
        expected_status_code: int,
        expected_body: Optional[dict],
):
    post_old_bin_set_request = {
        'name': 'old_bin_set',
        'time': {'start': '2019-01-01T00:00:01', 'end': '2019-01-01T00:00:03'},
        'bins': [1],
    }
    await common.add_bin_set(taxi_grocery_discounts, post_old_bin_set_request)

    post_bin_set_request = {
        'name': 'bin_set',
        'time': {'start': '2020-01-01T00:00:01', 'end': '2020-01-01T00:00:03'},
        'bins': [1],
    }
    await common.add_bin_set(taxi_grocery_discounts, post_bin_set_request)

    post_request = {
        'name': bin_set_name,
        'time': {'start': start, 'end': end},
        'bins': bins,
    }
    await _post_bin_set_check(
        taxi_grocery_discounts,
        post_request,
        expected_body,
        expected_status_code,
    )

    if bin_set_name in {'bin_set', 'old_bin_set'}:
        await _get_bin_set(
            taxi_grocery_discounts,
            bin_set_name,
            post_bin_set_request
            if bin_set_name == 'bin_set'
            else post_old_bin_set_request,
            200,
        )
    else:
        await _get_bin_set(
            taxi_grocery_discounts,
            bin_set_name,
            {
                'code': 'Not found',
                'message': f'Couldn\'t find bin set named {bin_set_name}.',
            },
            500,
        )
