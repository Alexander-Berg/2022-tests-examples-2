import datetime
import uuid

import pytest
import pytz

from tests_grocery_discounts import common

REVISION_ID = 1234
DISCOUNT_ID = '123'
DRAFT_ID = '1234_draft_id'
DISCOUNT = {
    'active_with_surge': False,
    'description': '1',
    'discount_meta': {
        'informer': {
            'color': 'cart_discounts_color',
            'picture': 'cart_discounts_picture',
            'text': 'cart_discounts_text',
        },
    },
    'values_with_schedules': [
        {
            'money_value': {
                'set_value': {
                    'maximum_discount': '10',
                    'value': '10.0',
                    'value_type': 'fraction',
                },
            },
            'schedule': {
                'intervals': [
                    {'day': [1, 2, 3, 4, 5, 6, 7], 'exclude': False},
                ],
                'timezone': 'LOCAL',
            },
        },
    ],
}
COMMON_MATCH_PATH = [
    {'condition_name': 'class', 'value': 'No class'},
    {'condition_name': 'experiment', 'value_type': 'Other'},
    {'condition_name': 'tag', 'value': 'tag1'},
    {'condition_name': 'has_yaplus', 'value_type': 'Other'},
    {'condition_name': 'active_with_surge', 'value_type': 'Other'},
    {'condition_name': 'application_name', 'value_type': 'Other'},
    {'condition_name': 'country', 'value_type': 'Other'},
    {'condition_name': 'city', 'value_type': 'Other'},
    {'condition_name': 'depot', 'value_type': 'Other'},
    {'condition_name': 'product_set', 'value': []},
    {'condition_name': 'orders_restriction', 'value_type': 'Other'},
]
PARAMETRIZE = pytest.mark.parametrize(
    'is_check, request_item, expected_status, '
    'expected_content, expected_discount',
    (
        pytest.param(
            True,
            {
                'hierarchy_name': 'cart_discounts',
                'discount_ids': [DISCOUNT_ID],
                'finished_at': '2020-02-02T00:00:00+00:00',
            },
            200,
            None,
            {
                'discount_data': {
                    'discounts': [
                        {
                            'discount': DISCOUNT,
                            'match_path': [
                                *COMMON_MATCH_PATH,
                                {
                                    'condition_name': 'active_period',
                                    'value': {
                                        'end': '2021-01-01T00:00:00+00:00',
                                        'is_end_utc': False,
                                        'is_start_utc': False,
                                        'start': '2020-01-01T09:00:01+00:00',
                                    },
                                },
                            ],
                            'meta_info': {
                                'create_draft_id': (
                                    'draft_id_check_add_rules_validation'
                                ),
                                'create_author': 'user',
                            },
                            'revision': REVISION_ID,
                            'discount_id': DISCOUNT_ID,
                        },
                    ],
                    'hierarchy_name': 'cart_discounts',
                },
            },
            id='is_check_with_finished_at',
        ),
        pytest.param(
            False,
            {
                'hierarchy_name': 'cart_discounts',
                'discount_ids': [DISCOUNT_ID],
                'finished_at': '2020-02-02T00:00:00+00:00',
            },
            200,
            None,
            {
                'discount_data': {
                    'discounts': [
                        {
                            'discount': DISCOUNT,
                            'match_path': [
                                *COMMON_MATCH_PATH,
                                {
                                    'condition_name': 'active_period',
                                    'value': {
                                        'end': '2020-02-02T00:00:00+00:00',
                                        'is_end_utc': True,
                                        'is_start_utc': False,
                                        'start': '2020-01-01T09:00:01+00:00',
                                    },
                                },
                            ],
                            'meta_info': {
                                'create_draft_id': (
                                    'draft_id_check_add_rules_validation'
                                ),
                                'create_author': 'user',
                                'end_time_draft_id': DRAFT_ID,
                            },
                            'revision': REVISION_ID,
                            'discount_id': DISCOUNT_ID,
                        },
                    ],
                    'hierarchy_name': 'cart_discounts',
                },
            },
            id='with_finished_at',
        ),
        pytest.param(
            True,
            {
                'discount_ids': [DISCOUNT_ID],
                'hierarchy_name': 'cart_discounts',
            },
            200,
            None,
            {
                'discount_data': {
                    'discounts': [
                        {
                            'discount': DISCOUNT,
                            'match_path': [
                                *COMMON_MATCH_PATH,
                                {
                                    'condition_name': 'active_period',
                                    'value': {
                                        'end': '2021-01-01T00:00:00+00:00',
                                        'is_end_utc': False,
                                        'is_start_utc': False,
                                        'start': '2020-01-01T09:00:01+00:00',
                                    },
                                },
                            ],
                            'meta_info': {
                                'create_draft_id': (
                                    'draft_id_check_add_rules_validation'
                                ),
                                'create_author': 'user',
                            },
                            'revision': REVISION_ID,
                            'discount_id': DISCOUNT_ID,
                        },
                    ],
                    'hierarchy_name': 'cart_discounts',
                },
            },
            id='is_check_without_finished_at',
        ),
        pytest.param(
            False,
            {'revisions': [REVISION_ID], 'hierarchy_name': 'cart_discounts'},
            200,
            None,
            {
                'discount_data': {
                    'discounts': [
                        {
                            'discount': DISCOUNT,
                            'match_path': [
                                *COMMON_MATCH_PATH,
                                {
                                    'condition_name': 'active_period',
                                    'value': {
                                        'end': '2020-01-02T00:05:00+00:00',
                                        'is_end_utc': True,
                                        'is_start_utc': False,
                                        'start': '2020-01-01T09:00:01+00:00',
                                    },
                                },
                            ],
                            'meta_info': {
                                'create_draft_id': (
                                    'draft_id_check_add_rules_validation'
                                ),
                                'create_author': 'user',
                                'end_time_draft_id': DRAFT_ID,
                            },
                            'revision': REVISION_ID,
                            'discount_id': DISCOUNT_ID,
                        },
                    ],
                    'hierarchy_name': 'cart_discounts',
                },
            },
            id='without_finished_at',
        ),
    ),
)


@PARAMETRIZE
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_v3_admin_match_discounts_finish_discounts(
        client,
        check_add_rules_validation,
        is_check,
        request_item,
        expected_status,
        expected_content,
        expected_discount,
        mocked_time,
):
    hierarchy_name = 'cart_discounts'
    # discount_id=123
    await check_add_rules_validation(
        False,
        {'revisions': [], 'update_existing_discounts': False},
        hierarchy_name,
        [
            common.VALID_ACTIVE_PERIOD,
            {'condition_name': 'tag', 'values': ['tag1', 'tag2']},
        ],
        common.small_cart_discount(),
        200,
        None,
    )
    # discount_id=124
    await check_add_rules_validation(
        False,
        {'revisions': [], 'update_existing_discounts': False},
        hierarchy_name,
        [
            common.VALID_ACTIVE_PERIOD,
            {'condition_name': 'country', 'values': ['RUS']},
        ],
        common.small_cart_discount(),
        200,
        None,
        series_id=str(uuid.uuid4()),
    )
    mocked_time.set(datetime.datetime(2020, 1, 2, tzinfo=pytz.utc))

    url = 'v3/admin/match-discounts/finish-discounts'
    if is_check:
        url += '/check'
    request = {'items': [request_item]}
    response = await client.post(
        url, headers=common.get_draft_headers(DRAFT_ID), json=request,
    )
    assert response.status_code == expected_status, response.json()
    if expected_status == 200 and is_check:
        lock_ids = [
            {'custom': True, 'id': str(revision)}
            for revision in request_item.get(
                'revisions', [REVISION_ID, REVISION_ID + 1],
            )
        ]
        data = response.json()
        data.get('lock_ids', []).sort(key=lambda x: x['id'])
        assert data == {'data': request, 'lock_ids': lock_ids}
    elif expected_content is not None:
        assert response.json() == expected_content
    response = await client.post(
        'v3/admin/match-discounts/load-discounts/',
        headers=common.get_draft_headers(),
        json={'hierarchy_name': hierarchy_name, 'revisions': [REVISION_ID]},
    )
    assert response.status_code == 200
    assert response.json() == expected_discount, response.json()
