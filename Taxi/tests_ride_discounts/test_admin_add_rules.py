import json
import pathlib
import random
from typing import List
from typing import Optional
import uuid

import discounts_match  # pylint: disable=E0401
import pytest

from tests_ride_discounts import common


def parametrize_add_rules():
    static = pathlib.Path(__file__).parent / 'static'
    path = static / 'default' / 'condition_descriptions.json'
    with open(path) as file:
        condition_descriptions = json.load(file)
    condition_names: dict = {}

    for description in condition_descriptions:
        hierarchy_name = description['name']
        if hierarchy_name in (
                'full_discounts',
                'experimental_discounts',
                'payment_method_discounts',
        ):
            continue
        for rule in description['conditions']:
            condition_name = rule['condition_name']
            if condition_name == 'zone':
                continue
            condition_names.setdefault(condition_name, []).append(
                hierarchy_name,
            )
    all_conditions_with_hierarchies = []
    for condition_name in sorted(condition_names.keys()):
        hierarchy_names = condition_names[condition_name]
        hierarchy_name = hierarchy_names[
            random.randint(0, len(hierarchy_names) - 1)
        ]
        all_conditions_with_hierarchies.append(
            (condition_name, hierarchy_name),
        )
    decorators = [
        pytest.mark.parametrize('has_exclusions', [True, False]),
        pytest.mark.parametrize(
            'values_type', list(discounts_match.ValuesType),
        ),
        pytest.mark.parametrize(
            'condition_name, hierarchy_name', all_conditions_with_hierarchies,
        ),
    ]

    def wrapper(func):
        for decorator in decorators:
            func = decorator(func)
        return discounts_match.mark_now(func)

    return wrapper


@pytest.mark.slow
@parametrize_add_rules()
@pytest.mark.geoareas(filename='geoareas_moscow.json')
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
    APPLICATION_MAP_PLATFORM={
        'some_application_name': 'some_application_platform',
    },
    APPLICATION_MAP_BRAND={'some_application_name': 'some_application_brand'},
)
async def test_admin_add_rules(
        client,
        check_add_rules,
        has_exclusions,
        values_type,
        hierarchy_name: str,
        condition_name: str,
        add_prioritized_entity,
):
    if condition_name == 'bins':
        await add_prioritized_entity(
            {
                'name': 'some_bins',
                'data': {
                    'prioritized_entity_type': 'bin_set',
                    'bins': ['600000', '600001'],
                    'active_period': {
                        'start': '2020-01-01T00:00:00',
                        'end': '2021-02-01T00:00:02',
                    },
                },
            },
        )

    await check_add_rules(
        hierarchy_name,
        condition_name,
        {'revisions': [], 'affected_discount_ids': []},
        False,
        has_exclusions,
        values_type,
        discount=common.make_discount(hierarchy_name=hierarchy_name),
        value_patterns={
            'order_type': 'to_airport',
            'zone': 'br_moscow',
            'point_b_is_set': '1',
            'intermediate_point_is_set': '0',
            'has_yaplus': '0',
            'geoarea_a_set': 'moscow',
        },
    )


@discounts_match.parametrize_is_check
@discounts_match.mark_now
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
async def test_admin_add_rules_with_parametrize_is_check(
        check_add_rules, is_check, additional_request_fields,
):
    condition_name = 'class'
    has_exclusions = 'False'
    values_type = discounts_match.ValuesType.TYPE
    hierarchy_name = 'full_money_discounts'

    await check_add_rules(
        hierarchy_name,
        condition_name,
        additional_request_fields,
        is_check,
        has_exclusions,
        values_type,
        value_patterns={
            'order_type': 'to_airport',
            'zone': 'br_moscow',
            'point_b_is_set': '1',
            'intermediate_point_is_set': '0',
            'has_yaplus': '0',
        },
    )


@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@discounts_match.parametrize_is_check
async def test_admin_add_rules_with_invalid_bin(
        additional_request_fields,
        is_check,
        check_add_rules_validation,
        get_condition_description,
        additional_rules,
):
    hierarchy_name = 'payment_method_money_discounts'
    condition_description = get_condition_description(hierarchy_name, 'bins')
    active_period_description = get_condition_description(
        hierarchy_name, 'active_period',
    )
    rules = [
        active_period_description.get_rule(),
        condition_description.get_rule(),
    ] + additional_rules
    await check_add_rules_validation(
        is_check,
        additional_request_fields,
        hierarchy_name,
        rules,
        None,
        400,
        {
            'code': 'Validation error',
            'message': 'Couldn\'t find bin set some_bins',
        },
    )


@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@discounts_match.parametrize_is_check
async def test_admin_add_rules_with_invalid_zone(
        is_check,
        additional_request_fields,
        get_condition_description,
        check_add_rules_validation,
):
    hierarchy_name = 'payment_method_money_discounts'
    condition_description = get_condition_description(hierarchy_name, 'zone')
    rules = [
        discounts_match.VALID_ACTIVE_PERIOD,
        condition_description.get_rule(
            discounts_match.ValuesType.TYPE, False, 'invalid',
        ),
    ]
    await check_add_rules_validation(
        is_check,
        additional_request_fields,
        hierarchy_name,
        rules,
        None,
        400,
        {
            'code': 'Validation error',
            'message': 'Missing geonode=\'invalid\' in agglomerations',
        },
    )


@pytest.mark.parametrize(
    'hierarchy_name',
    (
        pytest.param('experimental_money_discounts'),
        pytest.param('full_money_discounts'),
    ),
)
@pytest.mark.parametrize(
    'point_b_is_set_value',
    (
        pytest.param('100500', id='invalid_value'),
        pytest.param('0', id='point_b_is_actualy_set'),
    ),
)
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@discounts_match.parametrize_is_check
async def test_admin_add_rules_with_invalid_point_b_is_set(
        is_check,
        additional_request_fields,
        get_condition_description,
        check_add_rules_validation,
        point_b_is_set_value: str,
        hierarchy_name: str,
        additional_rules,
):
    condition_description = get_condition_description(
        hierarchy_name, 'point_b_is_set',
    )
    rules = [
        discounts_match.VALID_ACTIVE_PERIOD,
        condition_description.get_rule(
            discounts_match.ValuesType.TYPE, False, point_b_is_set_value,
        ),
        get_condition_description(hierarchy_name, 'geoarea_b_set').get_rule(
            discounts_match.ValuesType.TYPE, False,
        ),
    ] + additional_rules
    if point_b_is_set_value == '0':
        message = (
            f'point_b_is_set condition has value {point_b_is_set_value}, but '
            'geoarea_b_set condition present'
        )
    else:
        message = f'bool values must be 0 or 1: [{point_b_is_set_value}]'

    await check_add_rules_validation(
        is_check,
        additional_request_fields,
        hierarchy_name,
        rules,
        None,
        400,
        {'code': 'Validation error', 'message': message},
    )


@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@discounts_match.parametrize_is_check
async def test_admin_add_rules_with_invalid_geoarea_a_b_set(
        is_check,
        additional_request_fields,
        get_condition_description,
        check_add_rules_validation,
):
    hierarchy_name = 'full_money_discounts'
    condition_description = get_condition_description(hierarchy_name, 'zone')

    rules = [
        discounts_match.VALID_ACTIVE_PERIOD,
        condition_description.get_rule(
            discounts_match.ValuesType.TYPE, False, 'br_moscow',
        ),
        {'condition_name': 'geoarea_b_set', 'values': ['1']},
    ]

    await check_add_rules_validation(
        is_check,
        additional_request_fields,
        hierarchy_name,
        rules,
        None,
        400,
        {
            'code': 'Validation error',
            'message': (
                common.StartsWith(
                    'Exception in AnyOtherConditionsVectorFromGenerated for '
                    '\'geoarea_b_set\' :',
                )
            ),
        },
    )


DISCOUNTS_WITH_DISCOUNTS_COUNT = [
    {
        'min_discounts_count': 2,
        'discount_value': common.get_simple_discount_value(),
    },
    {
        'min_discounts_count': 10,
        'discount_value': common.get_simple_discount_value(),
    },
    {
        'min_discounts_count': 2,
        'discount_value': common.get_simple_discount_value(),
    },
]


@pytest.mark.parametrize(
    'condition_name',
    (pytest.param('intermediate_point_is_set'), pytest.param('has_yaplus')),
)
@pytest.mark.parametrize(
    'hierarchy_name',
    (
        pytest.param('experimental_money_discounts'),
        pytest.param('full_money_discounts'),
        pytest.param('payment_method_money_discounts'),
    ),
)
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@discounts_match.parametrize_is_check
async def test_admin_add_rules_with_invalid_intermediate_point_is_set(
        is_check,
        additional_request_fields,
        get_condition_description,
        check_add_rules_validation,
        hierarchy_name: str,
        condition_name: str,
        additional_rules,
):
    condition_description = get_condition_description(
        hierarchy_name, condition_name,
    )
    rules = [
        discounts_match.VALID_ACTIVE_PERIOD,
        condition_description.get_rule(
            discounts_match.ValuesType.TYPE, False, '100500',
        ),
    ] + additional_rules
    message = f'bool values must be 0 or 1: [{100500}]'

    await check_add_rules_validation(
        is_check,
        additional_request_fields,
        hierarchy_name,
        rules,
        None,
        400,
        {'code': 'Validation error', 'message': message},
    )


@pytest.mark.parametrize(
    'hierarchy_name',
    (
        pytest.param(
            'experimental_money_discounts', id='experimental_money_discounts',
        ),
        pytest.param('full_money_discounts', id='full_money_discounts'),
        pytest.param(
            'payment_method_money_discounts',
            id='payment_method_money_discounts',
        ),
    ),
)
@pytest.mark.parametrize(
    'values_with_schedules,discount_usage_restrictions',
    (
        pytest.param(
            [
                {
                    'money_value': common.make_discount_value(
                        None, DISCOUNTS_WITH_DISCOUNTS_COUNT,
                    ),
                    'schedule': common.DEFAULT_SCHEDULE,
                },
            ],
            [{'max_count': 1}],
            id='money_duplicate_discounts_count',
        ),
        pytest.param(
            [
                {
                    'cashback_value': common.make_discount_value(
                        None, DISCOUNTS_WITH_DISCOUNTS_COUNT,
                    ),
                    'schedule': common.DEFAULT_SCHEDULE,
                },
            ],
            [{'max_count': 1}],
            id='cashback_duplicate_discounts_count',
        ),
        pytest.param(
            [
                {
                    'money_value': common.make_discount_value(
                        None, DISCOUNTS_WITH_DISCOUNTS_COUNT,
                    ),
                    'cashback_value': common.make_discount_value(
                        None, DISCOUNTS_WITH_DISCOUNTS_COUNT,
                    ),
                    'schedule': common.DEFAULT_SCHEDULE,
                },
            ],
            [{'max_count': 1}],
            id='money_cashback_duplicate_discounts_count',
        ),
        pytest.param(
            [
                {
                    'money_value': common.make_discount_value(
                        None, DISCOUNTS_WITH_DISCOUNTS_COUNT,
                    ),
                    'cashback_value': common.make_discount_value(
                        None, DISCOUNTS_WITH_DISCOUNTS_COUNT,
                    ),
                    'schedule': common.DEFAULT_SCHEDULE,
                },
            ],
            None,
            id='money_cashback_duplicate_discounts_count',
        ),
    ),
)
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@discounts_match.parametrize_is_check
async def test_admin_add_rules_with_invalid_discounts_count(
        is_check,
        additional_request_fields,
        get_condition_description,
        check_add_rules_validation,
        values_with_schedules: List[dict],
        hierarchy_name: str,
        discount_usage_restrictions: Optional[List[dict]],
        additional_rules,
):
    rules = [discounts_match.VALID_ACTIVE_PERIOD] + additional_rules

    discount = common.make_discount(hierarchy_name=hierarchy_name)
    discount['values_with_schedules'] = values_with_schedules
    if discount_usage_restrictions is not None:
        message = 'Duplicate discounts count found 2'
        discount['discount_usage_restrictions'] = discount_usage_restrictions
    else:
        message = (
            'Discounts by discount usage count can\'t be set without discount '
            'usage restriction'
        )
    await check_add_rules_validation(
        is_check,
        additional_request_fields,
        hierarchy_name,
        rules,
        discount,
        400,
        {'code': 'Validation error', 'message': message},
    )


@pytest.mark.parametrize('series_id', (pytest.param('', id='empty_series_id')))
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@discounts_match.parametrize_is_check
async def test_admin_add_rules_with_invalid_series_id(
        is_check,
        additional_request_fields,
        get_condition_description,
        series_id,
        check_add_rules_validation,
):
    hierarchy_name = 'full_money_discounts'

    rules = [discounts_match.VALID_ACTIVE_PERIOD]

    await check_add_rules_validation(
        is_check,
        {'series_id': series_id},
        hierarchy_name,
        rules,
        None,
        400,
        None,
    )


@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@discounts_match.parametrize_is_check
async def test_admin_add_rules_with_intersecting_series(
        is_check,
        additional_request_fields,
        get_condition_description,
        check_add_rules_validation,
        reset_data_id,
):
    hierarchy_name = 'full_money_discounts'

    await check_add_rules_validation(
        False,
        {'affected_discount_ids': [], 'update_existing_discounts': False},
        hierarchy_name,
        [
            discounts_match.VALID_ACTIVE_PERIOD,
            {
                'condition_name': 'zone',
                'values': [
                    {
                        'name': 'br_moscow',
                        'type': 'geonode',
                        'is_prioritized': False,
                    },
                ],
            },
        ],
        None,
        200,
        None,
    )
    await check_add_rules_validation(
        is_check,
        {'affected_discount_ids': [], 'update_existing_discounts': False},
        hierarchy_name,
        [
            discounts_match.VALID_ACTIVE_PERIOD,
            {
                'condition_name': 'zone',
                'values': [
                    {
                        'name': 'br_moscow',
                        'type': 'geonode',
                        'is_prioritized': False,
                    },
                ],
            },
            {'condition_name': 'tariff', 'values': ['econom']},
        ],
        None,
        400,
        {
            'code': 'Validation error',
            'message': (
                'Intersecting rules with same series_id found. '
                f'ids: [{common.START_DATA_ID}]'
            ),
        },
    )


@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@discounts_match.parametrize_is_check
async def test_admin_add_rules_idempotency(
        client,
        is_check,
        additional_request_fields,
        get_condition_description,
        check_add_rules_validation,
        draft_headers,
):
    hierarchy_name = 'payment_method_money_discounts'
    condition_description = get_condition_description(hierarchy_name, 'zone')
    rules = [
        discounts_match.VALID_ACTIVE_PERIOD,
        condition_description.get_rule(
            discounts_match.ValuesType.TYPE, False, 'br_moscow',
        ),
    ]

    await check_add_rules_validation(
        is_check,
        additional_request_fields,
        hierarchy_name,
        rules,
        None,
        200,
        None,
        custom_draft_id='test_idempotency_add_rules',
    )

    headers = draft_headers.copy()
    headers['X-YaTaxi-Draft-Id'] = 'test_idempotency_add_rules'
    request: dict = {
        'rules': rules,
        'data': {
            'hierarchy_name': hierarchy_name,
            'discount': common.make_discount(hierarchy_name=hierarchy_name),
        },
        'series_id': common.SERIES_ID,
        'affected_discount_ids': [],
    }
    request.update(additional_request_fields)
    response = await client.post(
        'v1/admin/match-discounts/add-rules', request, headers=headers,
    )
    assert response.status_code == 200, response.text


@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'parent_name': 'br_root',
            'tariff_zones': ['test'],
        },
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
    ],
)
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@discounts_match.parametrize_is_check
async def test_admin_add_rules_tariff_zone_without_settings(
        client,
        is_check,
        additional_request_fields,
        get_condition_description,
        check_add_rules_validation,
        draft_headers,
        mockserver,
):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    def _tariff_zones(request):
        zones = [
            {
                'name': 'test',
                'time_zone': 'Europe/Moscow',
                'country': 'rus',
                'translation': 'test',
                'currency': 'RUB',
            },
        ]
        return {'zones': zones}

    hierarchy_name = 'payment_method_money_discounts'
    condition_description = get_condition_description(hierarchy_name, 'zone')
    rules = [
        condition_description.get_rule(
            discounts_match.ValuesType.TYPE, False, 'br_moscow',
        ),
    ]
    await check_add_rules_validation(
        is_check,
        additional_request_fields,
        hierarchy_name,
        rules + [discounts_match.VALID_ACTIVE_PERIOD],
        None,
        400,
        {
            'code': 'Validation error',
            'message': 'Tariff zone test has no tariff settings. Use utc time',
        },
    )

    await check_add_rules_validation(
        is_check,
        additional_request_fields,
        hierarchy_name,
        rules
        + [
            {
                'condition_name': 'active_period',
                'values': [
                    {
                        'start': '2020-01-01T09:00:01+00:00',
                        'is_start_utc': True,
                        'end': '2021-01-01T00:00:00+00:00',
                        'is_end_utc': True,
                    },
                ],
            },
        ],
        None,
        200,
        None,
    )


def _get_rules_for_trip_restriction(start: int, end: int):
    return [
        discounts_match.VALID_ACTIVE_PERIOD,
        {
            'condition_name': 'zone',
            'values': [
                {
                    'name': 'br_moscow',
                    'type': 'geonode',
                    'is_prioritized': False,
                },
            ],
        },
        {
            'condition_name': 'trips_restriction',
            'values': [{'allowed_trips_count': {'start': start, 'end': end}}],
        },
    ]


@pytest.mark.parametrize(
    'start, end, expected_code',
    (
        pytest.param(20, 29, 200, id='unique trips_restriction'),
        pytest.param(10, 19, 400, id='not unique trips_restriction'),
    ),
)
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.now('2019-01-01T00:00:00+00:00')
async def test_admin_add_rules_trips_restriction(
        check_add_rules_validation,
        add_discount,
        start: int,
        end: int,
        expected_code: int,
):
    hierarchy_name = 'full_money_discounts'
    await add_discount(
        hierarchy_name, _get_rules_for_trip_restriction(10, 19), uuid.uuid4(),
    )
    await check_add_rules_validation(
        False,
        {'affected_discount_ids': [], 'update_existing_discounts': False},
        hierarchy_name,
        _get_rules_for_trip_restriction(start, end),
        None,
        expected_code,
        None,
        series_id=str(uuid.uuid4()),
    )
