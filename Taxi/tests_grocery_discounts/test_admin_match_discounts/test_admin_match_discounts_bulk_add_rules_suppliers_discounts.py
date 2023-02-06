import pytest

from tests_grocery_discounts import common


async def _add_rules_bulk_suppliers(
        client,
        is_check,
        request,
        count_run_task=1,
        check_is_async=False,
        draft_id='',
):
    uri = 'v3/admin/match-discounts/add-suppliers-rules/bulk'
    if is_check:
        uri += '/check'
    draft_id = 'grocery_discounts_draft_id' + draft_id
    response = await client.post(
        uri, request, headers=common.get_draft_headers(draft_id=draft_id),
    )
    if check_is_async or not is_check:
        response_json = response.json()
        assert response_json == {
            'status': 'processing' if is_check else 'applying',
        }
        for _ in range(count_run_task):
            await client.run_task('bulk-adding-suppliers-rules-applier')
        response = await client.post(
            uri, request, headers=common.get_draft_headers(draft_id=draft_id),
        )
    return response


@pytest.mark.parametrize(
    'is_check, inject_error, count_run_task, expected_status, '
    'expected_error_content',
    (
        pytest.param(True, None, 1, 200, None, id='check_without_error'),
        pytest.param(False, None, 1, 200, None, id='apply_without_error'),
        pytest.param(
            False,
            'exception',
            1,
            400,
            {'code': 'Validation error', 'message': 'Injected error'},
            id='apply_with_error',
        ),
        pytest.param(
            False,
            'pg_exception',
            1,
            200,
            {'status': 'applying'},
            id='apply_with_pg_error',
        ),
        pytest.param(
            False,
            'pg_exception',
            4,
            400,
            {'code': 'Validation error', 'message': 'pg error'},
            id='apply_with_4_pg_error',
        ),
    ),
)
@pytest.mark.config(
    GROCERY_DISCOUNTS_USE_ASYNC_CHECK_IN_BULK_CREATE_DISCOUNTS=True,
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_add_bulk_suppliers_discounts_common(
        client,
        load_json,
        is_check,
        inject_error,
        count_run_task,
        expected_status,
        expected_error_content,
        testpoint,
) -> None:

    request = {
        'rules': [
            common.VALID_ACTIVE_PERIOD,
            {'condition_name': 'country', 'values': ['RUS']},
            {'condition_name': 'city', 'values': ['213']},
        ],
        'product_discounts': [
            {
                'discount_value': '20',
                'discount_type': 'fraction',
                'products': [
                    'first_product',
                    'second_product',
                    'third_product',
                ],
            },
            {
                'discount_value': '30',
                'discount_type': 'absolute',
                'products': ['other_product'],
            },
        ],
        'description': 'test_bulk',
        'revisions': [],
        'schedule': common.DEFAULT_SCHEDULE,
        'update_existing_discounts': False,
    }

    @testpoint('add_bulk_rules')
    def _inject_error_testpoint(data):
        return {'inject': inject_error}

    response = await _add_rules_bulk_suppliers(
        client, is_check, request, count_run_task, True,
    )

    if expected_error_content:
        assert response.json() == expected_error_content
        return
    assert response.status_code == 200
    response_json = response.json()
    if is_check:
        expected_json = load_json('response.json')
        assert response_json == expected_json
    else:
        assert response_json == {'status': 'completed'}
        search_data = {
            'hierarchy_name': 'suppliers_discounts',
            'conditions': [common.VALID_ACTIVE_PERIOD],
        }
        search_response = await client.post(
            '/v3/admin/match-discounts/search-rules',
            json=search_data,
            headers=common.get_headers(),
        )
        assert search_response.status_code == 200

        search_expected_json = load_json('search_response.json')
        assert search_response.json() == search_expected_json


@pytest.mark.parametrize(
    'is_check',
    (pytest.param(True, id='check'), pytest.param(False, id='not_check')),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_add_bulk_suppliers_discounts_update_existing_discounts(
        client, load_json, is_check,
) -> None:

    request = {
        'rules': [
            common.VALID_ACTIVE_PERIOD,
            {'condition_name': 'country', 'values': ['RUS']},
            {'condition_name': 'city', 'values': ['213']},
        ],
        'product_discounts': [
            {
                'discount_value': '20',
                'discount_type': 'fraction',
                'products': [
                    'first_product',
                    'second_product',
                    'third_product',
                ],
            },
            {
                'discount_value': '30',
                'discount_type': 'absolute',
                'products': ['other_product'],
            },
        ],
        'description': 'test_bulk',
        'revisions': [],
        'schedule': common.DEFAULT_SCHEDULE,
        'update_existing_discounts': False,
    }

    await _add_rules_bulk_suppliers(client, is_check, request, draft_id='1')

    request = {
        'rules': [
            common.VALID_ACTIVE_PERIOD,
            {'condition_name': 'country', 'values': ['RUS']},
            {'condition_name': 'city', 'values': ['213']},
        ],
        'product_discounts': [
            {
                'series_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                'discount_value': '20',
                'discount_type': 'fraction',
                'products': ['first_product', 'third_product'],
            },
            {
                'series_id': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
                'discount_value': '30',
                'discount_type': 'absolute',
                'products': ['other_product'],
            },
        ],
        'description': 'test_bulk',
        'revisions': [],
        'schedule': common.DEFAULT_SCHEDULE,
        'update_existing_discounts': True,
    }

    if is_check:
        request.pop('revisions')
    else:
        request['revisions'] = [1237, 1234, 1236]

    response = await _add_rules_bulk_suppliers(
        client, is_check, request, draft_id='2',
    )

    assert response.status_code == 200

    response_json = response.json()
    if is_check:
        response_json['data'].pop('revisions')
        response_json.pop('lock_ids')
        expected_json = load_json('response.json')
        assert response_json == expected_json
    else:
        assert response_json == {'status': 'completed'}, response_json

        search_data = {
            'hierarchy_name': 'suppliers_discounts',
            'conditions': [common.VALID_ACTIVE_PERIOD],
        }
        search_response = await client.post(
            '/v3/admin/match-discounts/search-rules',
            json=search_data,
            headers=common.get_headers(),
        )
        assert search_response.status_code == 200

        search_expected_json = load_json('search_response.json')
        assert search_response.json() == search_expected_json


@pytest.mark.parametrize(
    'is_check',
    (pytest.param(True, id='check'), pytest.param(False, id='not_check')),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_add_bulk_suppliers_discounts_intersection_error(
        client, is_check,
) -> None:

    request = {
        'rules': [
            common.VALID_ACTIVE_PERIOD,
            {'condition_name': 'country', 'values': ['RUS']},
            {'condition_name': 'city', 'values': ['213']},
        ],
        'product_discounts': [
            {
                'series_id': '260e0c5a-f36b-11eb-9a03-0242ac130003',
                'discount_value': '20',
                'discount_type': 'fraction',
                'products': [
                    'first_product',
                    'second_product',
                    'third_product',
                ],
            },
            {
                'series_id': '260e0eb2-f36b-11eb-9a03-0242ac130003',
                'discount_value': '30',
                'discount_type': 'absolute',
                'products': ['other_product'],
            },
        ],
        'description': 'test_bulk',
        'revisions': [],
        'schedule': common.DEFAULT_SCHEDULE,
        'update_existing_discounts': False,
    }

    await _add_rules_bulk_suppliers(client, is_check, request, draft_id='1')

    request = {
        'rules': [
            {
                'condition_name': 'active_period',
                'values': [
                    {
                        'start': '2020-01-01T18:00:01+00:00',
                        'is_start_utc': False,
                        'is_end_utc': False,
                        'end': '2021-01-01T00:00:00+00:00',
                    },
                ],
            },
            {'condition_name': 'country', 'values': ['RUS']},
            {'condition_name': 'city', 'values': ['213']},
        ],
        'product_discounts': [
            {
                'series_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                'discount_value': '25',
                'discount_type': 'fraction',
                'products': ['first_product', 'third_product'],
            },
            {
                'series_id': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
                'discount_value': '35',
                'discount_type': 'absolute',
                'products': ['first_product', 'other_product'],
            },
        ],
        'description': 'test_bulk',
        'revisions': [],
        'schedule': common.DEFAULT_SCHEDULE,
        'update_existing_discounts': True,
    }

    if is_check:
        request.pop('revisions')
    else:
        request['revisions'] = [1237, 1238, 1234, 1236]

    response = await _add_rules_bulk_suppliers(
        client, is_check, request, draft_id='2',
    )

    assert response.status_code == 400
    response_json = response.json()
    error_response = {
        'code': 'Validation error',
        'message': 'Some added discounts intersect each other',
    }

    assert response_json == error_response
