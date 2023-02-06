import discounts_match  # pylint: disable=E0401
import pytest

from tests_ride_discounts import common


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.parametrize(
    'closed_at, expected_status, expected_content',
    (
        pytest.param(
            '2019-01-01T00:02:00+00:00',
            400,
            {
                'code': 'Validation error',
                'message': 'closed_at must be more than now + 300s seconds',
            },
            id='400',
        ),
        pytest.param(
            '2019-01-01T00:06:00+00:00',
            200,
            {'status': 'completed'},
            id='200',
        ),
    ),
)
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.config(
    USERVICE_AGGLOMERATIONS_CACHE_SETTINGS={
        '__default__': {
            'enabled': True,
            'log_errors': True,
            'verify_on_updates': True,
        },
    },
    APPLICATION_MAP_DISCOUNTS={
        'some_application_name': 'some_application_type',
    },
)
@pytest.mark.parametrize(
    'url',
    [
        pytest.param(
            '/v1/admin/match-discounts/replace-smart-discounts/check',
            id='check',
        ),
    ],
)
@pytest.mark.usefixtures('reset_data_id', 'reset_revision')
async def test_admin_replace_smart_discounts_not_async(
        client,
        url,
        check_add_rules,
        default_discount,
        draft_headers,
        closed_at,
        expected_status,
        expected_content,
):
    await check_add_rules(
        hierarchy_name='full_money_discounts',
        condition_name='zone',
        additional_request_fields={'affected_discount_ids': []},
        is_check=False,
        has_exclusions=False,
        values_type=discounts_match.ValuesType.TYPE,
        value_patterns={'zone': 'br_moscow'},
    )
    body = {
        'hierarchy_name': 'full_money_discounts',
        'to_close': {
            'discount_ids': [common.START_DATA_ID],
            'closed_at': closed_at,
        },
        'to_add': [
            {
                'rules': [
                    discounts_match.VALID_ACTIVE_PERIOD,
                    {
                        'condition_name': 'zone',
                        'values': [
                            {
                                'name': 'moscow',
                                'type': 'tariff_zone',
                                'is_prioritized': False,
                            },
                        ],
                    },
                ],
                'data': default_discount,
                'series_id': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
            },
            {
                'rules': [
                    discounts_match.VALID_ACTIVE_PERIOD,
                    {
                        'condition_name': 'zone',
                        'values': [
                            {
                                'name': 'br_moscow',
                                'type': 'geonode',
                                'is_prioritized': True,
                            },
                        ],
                    },
                ],
                'data': default_discount,
                'series_id': 'abbbbbbb-abbb-bbbb-bbbb-bbbbbbbbbbbb',
            },
        ],
    }
    response = await client.post(url, headers=draft_headers, json=body)
    if expected_status == 200 and 'check' in url:
        expected_content['data'] = body
        expected_content['lock_ids'] = [
            {'custom': True, 'id': 'ride-discounts' + common.START_DATA_ID},
        ]
    assert response.json() == expected_content


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.parametrize(
    'closed_at, inject_error, count_run_task, '
    'expected_status, expected_content',
    (
        pytest.param(
            '2019-01-01T00:02:00+00:00',
            None,
            1,
            400,
            {
                'code': 'Validation error',
                'message': 'closed_at must be more than now + 300s seconds',
            },
            id='in_2_minutes',
        ),
        pytest.param(
            '2019-01-01T00:06:00+00:00',
            None,
            1,
            200,
            {'status': 'completed'},
            id='in_6_minutes_without_error',
        ),
        pytest.param(
            '2019-01-01T00:06:00+00:00',
            'exception',
            1,
            400,
            {'code': 'Validation error', 'message': 'Injected error'},
            id='in_6_minutes_with_error',
        ),
        pytest.param(
            '2019-01-01T00:06:00+00:00',
            'pg_exception',
            1,
            200,
            {'status': 'in_progress'},
            id='in_6_minutes_with_one_error',
        ),
        pytest.param(
            '2019-01-01T00:06:00+00:00',
            'pg_exception',
            4,
            400,
            {'code': 'Validation error', 'message': 'pg error'},
            id='in_6_minutes_with_4_error',
        ),
    ),
)
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.config(
    RIDE_DISCOUNTS_USE_ASYNC_CHECK_IN_BULK_CREATE_DISCOUNTS=True,
    USERVICE_AGGLOMERATIONS_CACHE_SETTINGS={
        '__default__': {
            'enabled': True,
            'log_errors': True,
            'verify_on_updates': True,
        },
    },
    APPLICATION_MAP_DISCOUNTS={
        'some_application_name': 'some_application_type',
    },
    APPLICATION_MAP_PLATFORM={
        'some_application_name': 'some_application_platform',
    },
    APPLICATION_MAP_BRAND={'some_application_name': 'some_application_brand'},
)
@pytest.mark.parametrize(
    'url',
    [
        pytest.param(
            '/v1/admin/match-discounts/replace-smart-discounts', id='apply',
        ),
        pytest.param(
            '/v1/admin/match-discounts/replace-smart-discounts/check',
            id='check',
        ),
    ],
)
@pytest.mark.usefixtures('reset_data_id', 'reset_revision')
async def test_admin_replace_smart_discounts(
        client,
        url,
        check_add_rules,
        default_discount,
        draft_headers,
        closed_at,
        expected_status,
        expected_content,
        inject_error,
        testpoint,
        count_run_task,
):
    await check_add_rules(
        hierarchy_name='full_money_discounts',
        condition_name='zone',
        additional_request_fields={'affected_discount_ids': []},
        is_check=False,
        has_exclusions=False,
        values_type=discounts_match.ValuesType.TYPE,
        value_patterns={'zone': 'br_moscow'},
    )
    body = {
        'hierarchy_name': 'full_money_discounts',
        'to_close': {
            'discount_ids': [common.START_DATA_ID],
            'closed_at': closed_at,
        },
        'to_add': [
            {
                'rules': [
                    discounts_match.VALID_ACTIVE_PERIOD,
                    {
                        'condition_name': 'zone',
                        'values': [
                            {
                                'name': 'moscow',
                                'type': 'tariff_zone',
                                'is_prioritized': False,
                            },
                        ],
                    },
                ],
                'data': default_discount,
                'series_id': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
            },
            {
                'rules': [
                    discounts_match.VALID_ACTIVE_PERIOD,
                    {
                        'condition_name': 'zone',
                        'values': [
                            {
                                'name': 'br_moscow',
                                'type': 'geonode',
                                'is_prioritized': True,
                            },
                        ],
                    },
                ],
                'data': default_discount,
                'series_id': 'abbbbbbb-abbb-bbbb-bbbb-bbbbbbbbbbbb',
            },
        ],
    }
    response = await client.post(url, headers=draft_headers, json=body)
    assert response.status == 200
    in_progress_status = 'processing' if 'check' in url else 'applying'
    if 'check' in url:
        expected = {
            'status': in_progress_status,
            'lock_ids': [
                {
                    'custom': True,
                    'id': 'ride-discounts' + common.START_DATA_ID,
                },
            ],
        }
    else:
        expected = {'status': in_progress_status}
    assert response.json() == expected

    @testpoint('replace_smart_discounts')
    def _inject_error_testpoint(data):
        return {'inject': inject_error}

    for _ in range(count_run_task):
        await client.run_task('bulk-adding-rules-applier')

    response = await client.post(url, headers=draft_headers, json=body)
    in_progress = expected_content.get('status') == 'in_progress'
    if in_progress:
        expected_content = {'status': in_progress_status}

    if expected_status == 200 and 'check' in url:
        if not in_progress:
            expected_content['data'] = body
        expected_content['lock_ids'] = [
            {'custom': True, 'id': 'ride-discounts' + common.START_DATA_ID},
        ]
    assert response.json() == expected_content
