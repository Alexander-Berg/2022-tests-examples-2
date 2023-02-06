import datetime

import pytest

from tests_eats_discounts import common

START_BEFORE = '2020-01-01T09:00:00+00:00'
START_AT = '2020-01-01T09:00:01+00:00'
START_AFTER = '2020-01-01T09:00:02+00:00'

END_BEFORE = '2020-12-31T23:59:59+00:00'
END_AT = '2021-01-01T00:00:00+00:00'
END_AFTER = '2021-01-01T00:00:10+00:00'


def _count_affected_revisions(
        hierarchy_name: str,
        start_str: str,
        end_str: str,
        initial_add_rules_data: dict,
) -> int:
    count = 0
    end = datetime.datetime.strptime(end_str, common.DATETIME_FORMAT)

    for data in initial_add_rules_data[hierarchy_name]:
        for rule in data['rules']:
            if rule['condition_name'] == 'active_period':
                for value in rule['values']:
                    value_start = datetime.datetime.strptime(
                        value['start'], common.DATETIME_FORMAT,
                    )
                    if value_start < end:
                        count += 1
                break
    return count


@pytest.mark.parametrize(
    'update_existing_discounts',
    (
        pytest.param(True, id='update_existing_discounts'),
        pytest.param(False, id='not_update_existing_discounts'),
    ),
)
@pytest.mark.parametrize(
    'end',
    (
        pytest.param(END_BEFORE, id='end_before'),
        pytest.param(END_AT, id='end_at'),
        pytest.param(END_AFTER, id='end_after'),
    ),
)
@pytest.mark.parametrize(
    'start',
    (
        pytest.param(START_BEFORE, id='start_before'),
        pytest.param(START_AT, id='start_at'),
        pytest.param(START_AFTER, id='start_after'),
    ),
)
@pytest.mark.parametrize(
    'hierarchy_name',
    (
        pytest.param('menu_discounts', id='menu_discounts'),
        pytest.param('cart_discounts', id='cart_discounts'),
        pytest.param(
            'payment_method_discounts', id='payment_method_discounts',
        ),
    ),
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_add_rules_check_collisions(
        client,
        start: str,
        end: str,
        hierarchy_name: str,
        update_existing_discounts: bool,
        add_rules,
        check_add_rules_validation,
):
    await common.init_bin_sets(client)
    hierarchy_names = frozenset((hierarchy_name,))
    initial_add_rules_data = common.get_add_rules_data(None, hierarchy_names)

    await add_rules(initial_add_rules_data, {'series_id': common.SERIES_ID})

    if update_existing_discounts:
        expected_status_code = 200
        expected_response = None
        expected_revisions_count = _count_affected_revisions(
            hierarchy_name, start, end, initial_add_rules_data,
        )
    else:
        expected_status_code = 400
        expected_response = {
            'code': 'Validation error',
            'message': (
                'Flag \'update_existing_discounts\' is false but '
                'rules adding affects some rules'
            ),
        }
        expected_revisions_count = 0

    add_rules_data = common.get_add_rules_data(
        {
            'condition_name': 'active_period',
            'values': [
                {
                    'start': start,
                    'end': end,
                    'is_start_utc': True,
                    'is_end_utc': True,
                },
            ],
        },
        hierarchy_names,
    )
    await check_add_rules_validation(
        True,
        {
            'update_existing_discounts': update_existing_discounts,
            'series_id': common.SERIES_ID,
        },
        hierarchy_name,
        add_rules_data[hierarchy_name][0]['rules'],
        add_rules_data[hierarchy_name][0]['discount'],
        expected_status_code,
        expected_response,
        expected_revisions_count,
    )


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_add_rules_collisions_revisions_mismatch(
        client,
        draft_headers,
        add_rules,
        check_add_rules_validation,
        load_json,
):

    hierarchy_name = 'menu_discounts'
    start = START_BEFORE
    end = END_AFTER
    await common.init_bin_sets(client)
    hierarchy_names = frozenset((hierarchy_name,))
    initial_add_rules_data = common.get_add_rules_data(None, hierarchy_names)
    await add_rules(initial_add_rules_data, {'series_id': common.SERIES_ID})

    add_rules_data = common.get_add_rules_data(
        {
            'condition_name': 'active_period',
            'values': [
                {
                    'start': start,
                    'end': end,
                    'is_start_utc': True,
                    'is_end_utc': True,
                },
            ],
        },
        hierarchy_names,
        '3',
    )

    admin_match_discounts_request = load_json(
        'admin_match_discounts_request.json',
    )
    admin_match_discounts_response = load_json(
        'admin_match_discounts_response.json',
    )

    affected_revisions_count = _count_affected_revisions(
        hierarchy_name, start, end, initial_add_rules_data,
    )
    await check_add_rules_validation(
        False,
        {'revisions': [], 'series_id': common.SERIES_ID},
        hierarchy_name,
        add_rules_data[hierarchy_name][0]['rules'],
        add_rules_data[hierarchy_name][0]['discount'],
        400,
        {
            'code': 'Validation error',
            'message': (
                'Number of expected affected revisions '
                f'0 does not match {affected_revisions_count}'
            ),
        },
    )

    await common.check_admin_match_discounts(
        client,
        draft_headers,
        admin_match_discounts_request,
        admin_match_discounts_response,
        200,
    )


@pytest.mark.parametrize(
    'start, end, admin_match_discounts_response_file',
    (
        pytest.param(
            START_BEFORE,
            END_BEFORE,
            'start_before_end_before_response.json',
            id='start_before_end_before',
        ),
        pytest.param(
            START_BEFORE,
            END_AT,
            'start_before_end_at_response.json',
            id='start_before_end_at',
        ),
        pytest.param(
            START_BEFORE,
            END_AFTER,
            'start_before_end_after_response.json',
            id='start_before_end_after',
        ),
        pytest.param(
            START_AT,
            END_BEFORE,
            'start_at_end_before_response.json',
            id='start_at_end_before',
        ),
        pytest.param(
            START_AT,
            END_AT,
            'start_at_end_at_response.json',
            id='start_at_end_at',
        ),
        pytest.param(
            START_AT,
            END_AFTER,
            'start_at_end_after_response.json',
            id='start_at_end_after',
        ),
        pytest.param(
            START_AFTER,
            END_BEFORE,
            'start_after_end_before_response.json',
            id='start_after_end_before',
        ),
        pytest.param(
            START_AFTER,
            END_AT,
            'start_after_end_at_response.json',
            id='start_after_end_at',
        ),
        pytest.param(
            START_AFTER,
            END_AFTER,
            'start_after_end_after_response.json',
            id='start_after_end_after',
        ),
    ),
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_add_rules_collisions(
        client,
        draft_headers,
        add_rules,
        load_json,
        check_add_rules_validation,
        start: str,
        end: str,
        admin_match_discounts_response_file: str,
):
    hierarchy_name = 'menu_discounts'
    admin_match_discounts_request = load_json(
        'admin_match_discounts_request.json',
    )
    admin_match_discounts_response = load_json(
        admin_match_discounts_response_file,
    )
    await common.init_bin_sets(client)
    hierarchy_names = frozenset((hierarchy_name,))
    initial_add_rules_data = common.get_add_rules_data(None, hierarchy_names)
    await add_rules(initial_add_rules_data, {'series_id': common.SERIES_ID})

    add_rules_data = common.get_add_rules_data(
        {
            'condition_name': 'active_period',
            'values': [
                {
                    'start': start,
                    'end': end,
                    'is_start_utc': True,
                    'is_end_utc': True,
                },
            ],
        },
        hierarchy_names,
        '3',
    )

    affected_revisions_count = _count_affected_revisions(
        hierarchy_name, start, end, initial_add_rules_data,
    )
    revisions = await check_add_rules_validation(
        True,
        {'update_existing_discounts': True, 'series_id': common.SERIES_ID},
        hierarchy_name,
        add_rules_data[hierarchy_name][0]['rules'],
        add_rules_data[hierarchy_name][0]['discount'],
        200,
        None,
        affected_revisions_count,
    )

    await check_add_rules_validation(
        False,
        {'revisions': revisions, 'series_id': common.SERIES_ID},
        hierarchy_name,
        add_rules_data[hierarchy_name][0]['rules'],
        add_rules_data[hierarchy_name][0]['discount'],
        200,
        None,
    )

    await common.check_admin_match_discounts(
        client,
        draft_headers,
        admin_match_discounts_request,
        admin_match_discounts_response,
        200,
    )
