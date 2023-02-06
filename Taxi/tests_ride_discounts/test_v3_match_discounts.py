import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
import uuid

import pytest

from tests_ride_discounts import common


PHONE_ID = '1' * 24
WRITE_MAX_DISCOUNTS_FOR_TARIFF_TO_LOG = pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name=(
        'ride_discounts_match_discounts_need_'
        'calculate_max_total_count_discounts'
    ),
    consumers=['ride-discounts/match-discounts'],
    default_value={'enabled': True},
    is_config=False,
)
NOT_NEED_RETURN_DISCOUNTS = pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='ride_discounts_need_return_discounts',
    consumers=['ride-discounts/match-discounts'],
    default_value={'need_return': False},
    is_config=True,
)
NEED_RETURN_DISCOUNTS = pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='ride_discounts_need_return_discounts',
    consumers=['ride-discounts/match-discounts'],
    default_value={'need_return': True},
    is_config=True,
)
RULES = [
    {'condition_name': 'tariff', 'values': ['econom']},
    {'condition_name': 'tag', 'values': ['user_tag']},
    {
        'condition_name': 'surge_range',
        'values': [{'start': '0.0', 'end': '1.21'}],
    },
    {
        'condition_name': 'zone',
        'values': [
            {'is_prioritized': False, 'name': 'moscow', 'type': 'tariff_zone'},
        ],
    },
    {
        'condition_name': 'active_period',
        'values': [
            {
                'end': '2021-07-08T15:00:00+00:00',
                'is_end_utc': True,
                'is_start_utc': True,
                'start': '2021-06-25T18:00:00+00:00',
            },
        ],
    },
    {
        'condition_name': 'trips_restriction',
        'values': [{'allowed_trips_count': {'start': 5, 'end': 10}}],
    },
]


def _get_orders_response(count: int):
    return {
        'data': [
            {
                'identity': {
                    'type': 'phone_id',
                    'value': '111111111111111111111111',
                },
                'counters': [
                    {
                        'value': count,
                        'counted_from': '2017-01-01T00:00:00',
                        'counted_to': '2018-01-01T00:00:00',
                        'properties': [
                            {'name': 'brand', 'value': 'yango'},
                            {'name': 'payment_type', 'value': 'card'},
                            {'name': 'tariff_class', 'value': 'econom'},
                        ],
                    },
                ],
            },
        ],
    }


DEFAULT_TRIPS_RESTRICTIONS = {'allowed_trips_count': {'start': 5, 'end': 10}}
DEFAULT_ORDERS_RESPONSE = _get_orders_response(7)


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.usefixtures('reset_data_id')
@pytest.mark.parametrize(
    'count_usages, should_return_discount, additional_discount_data, '
    'discount_trips_restrictions, discount_usage_restrictions, request_time, '
    'maximum_budget_per_person, user_statistics',
    (
        pytest.param(
            1,
            True,
            {},
            DEFAULT_TRIPS_RESTRICTIONS,
            None,
            '2021-06-27T18:00:00+03:00',
            None,
            DEFAULT_ORDERS_RESPONSE,
            id='1_has_not_usages',
        ),
        pytest.param(
            1,
            True,
            {},
            DEFAULT_TRIPS_RESTRICTIONS,
            None,
            '2021-06-27T18:00:00+03:00',
            None,
            DEFAULT_ORDERS_RESPONSE,
            marks=NEED_RETURN_DISCOUNTS,
            id='1_has_not_usages_and_need_return_discounts',
        ),
        pytest.param(
            1,
            False,
            {},
            DEFAULT_TRIPS_RESTRICTIONS,
            None,
            '2021-06-27T18:00:00+03:00',
            None,
            DEFAULT_ORDERS_RESPONSE,
            marks=NOT_NEED_RETURN_DISCOUNTS,
            id='1_has_not_usages_and_not_return_discounts',
        ),
        pytest.param(
            0,
            True,
            {'usage_restrictions': {'current': 0, 'maximum': 1}},
            DEFAULT_TRIPS_RESTRICTIONS,
            [{'max_count': 1}],
            '2021-06-27T18:00:00+03:00',
            None,
            DEFAULT_ORDERS_RESPONSE,
            id='0_usages',
        ),
        pytest.param(
            1,
            False,
            {},
            DEFAULT_TRIPS_RESTRICTIONS,
            [{'max_count': 1}],
            '2021-06-27T18:00:00+03:00',
            None,
            DEFAULT_ORDERS_RESPONSE,
            id='1_usages',
        ),
        pytest.param(
            2,
            True,
            {'budget_per_person': {'spent': 200, 'maximum': 201}},
            DEFAULT_TRIPS_RESTRICTIONS,
            None,
            '2021-06-27T18:00:00+03:00',
            [{'value': 201, 'interval': {'type': 'last_days', 'count': 1}}],
            DEFAULT_ORDERS_RESPONSE,
            marks=WRITE_MAX_DISCOUNTS_FOR_TARIFF_TO_LOG,
            id='2_budget_201',
        ),
        pytest.param(
            2,
            False,
            {},
            DEFAULT_TRIPS_RESTRICTIONS,
            None,
            '2021-06-27T18:00:00+03:00',
            [{'value': 200}],
            DEFAULT_ORDERS_RESPONSE,
            id='2_budget_200',
        ),
        pytest.param(
            1,
            False,
            {},
            DEFAULT_TRIPS_RESTRICTIONS,
            None,
            '2021-06-27T18:00:00+03:00',
            None,
            {'data': []},
            id='trips_restriction_orders_empty',
        ),
        pytest.param(
            1,
            False,
            {},
            DEFAULT_TRIPS_RESTRICTIONS,
            None,
            '2021-06-27T18:00:00+03:00',
            None,
            _get_orders_response(3),
            id='trips_restriction_false_1',
        ),
        pytest.param(
            1,
            False,
            {},
            DEFAULT_TRIPS_RESTRICTIONS,
            None,
            '2021-06-27T18:00:00+03:00',
            None,
            _get_orders_response(15),
            id='trips_restriction_false_2',
        ),
        pytest.param(
            1,
            True,
            {},
            DEFAULT_TRIPS_RESTRICTIONS,
            None,
            '2021-06-27T18:00:00+03:00',
            None,
            DEFAULT_ORDERS_RESPONSE,
            id='trips_restriction_experimant_off',
            marks=pytest.mark.experiments3(
                filename='trips_restriction_experiment_off.json',
            ),
        ),
        pytest.param(
            1,
            True,
            {},
            DEFAULT_TRIPS_RESTRICTIONS,
            None,
            '2021-06-27T18:00:00+03:00',
            None,
            DEFAULT_ORDERS_RESPONSE,
            id='trips_restriction_experimant_on',
            marks=pytest.mark.experiments3(
                filename='trips_restriction_experiment_on.json',
            ),
        ),
        pytest.param(
            1,
            False,
            {},
            DEFAULT_TRIPS_RESTRICTIONS,
            None,
            '2021-06-27T18:00:00+03:00',
            None,
            _get_orders_response(15),
            id='trips_restriction_experimant_off',
            marks=pytest.mark.experiments3(
                filename='trips_restriction_experiment_off.json',
            ),
        ),
        pytest.param(
            1,
            False,
            {},
            DEFAULT_TRIPS_RESTRICTIONS,
            None,
            '2021-06-27T18:00:00+03:00',
            None,
            _get_orders_response(15),
            id='trips_restriction_experimant_on',
            marks=pytest.mark.experiments3(
                filename='trips_restriction_experiment_on.json',
            ),
        ),
        pytest.param(
            1,
            False,
            {},
            {'allowed_trips_count': {'start': 10}},
            None,
            '2021-06-27T18:00:00+03:00',
            None,
            DEFAULT_ORDERS_RESPONSE,
            id='trips_restriction_open_range_fail',
        ),
        pytest.param(
            1,
            True,
            {},
            {'allowed_trips_count': {'start': 10}},
            None,
            '2021-06-27T18:00:00+03:00',
            None,
            _get_orders_response(400),
            id='trips_restriction_open_range_true',
        ),
    ),
)
@pytest.mark.parametrize(
    'hierarchy_name, is_money',
    (
        ('full_money_discounts', True),
        ('experimental_cashback_discounts', False),
    ),
)
@pytest.mark.config(
    RIDE_DISCOUNTS_FETCHING_DATA_SETTINGS={
        'discount_usages': {'enabled': True},
        'user_statistics': {'enabled': True},
    },
)
async def test_v3_match_discounts(
        client,
        mockserver,
        add_discount,
        mocked_time,
        stq_runner,
        count_usages: int,
        should_return_discount: bool,
        additional_discount_data: dict,
        discount_trips_restrictions: Dict[str, dict],
        discount_usage_restrictions: Optional[List[Dict[str, Any]]],
        request_time: str,
        maximum_budget_per_person: Optional[List[Dict[str, Any]]],
        user_statistics: Optional[Dict[str, Any]],
        hierarchy_name,
        is_money,
):
    @mockserver.json_handler('/user-statistics/v1/orders')
    def v1_orders(request):
        return user_statistics

    additional_discount_properties = {
        'trips_restriction': [discount_trips_restrictions],
    }
    if discount_usage_restrictions is not None:
        additional_discount_properties[
            'discount_usage_restrictions'
        ] = discount_usage_restrictions
    if maximum_budget_per_person is not None:
        additional_discount_properties[
            'maximum_budget_per_person'
        ] = maximum_budget_per_person
    await add_discount(
        hierarchy_name=hierarchy_name,
        rules=RULES,
        discount=common.make_discount(
            additional_properties=additional_discount_properties,
            hierarchy_name=hierarchy_name,
        ),
    )
    for _ in range(count_usages):
        kwargs: Dict[str, Any] = {
            'order_id': str(uuid.uuid4()),
            'discount_id': '123',
            'personal_phone_id': 'personal_phone_id',
            'type': 'ADD',
            'time': '2021-06-26T23:00:00+00:00',  # at 27 in Moscow time
        }
        await stq_runner.ride_discounts_discount_usages_by_id.call(
            task_id=str(uuid.uuid4()), kwargs=kwargs,
        )
        kwargs['type'] = 'FINISH'
        kwargs['discount_value'] = -100
        await stq_runner.ride_discounts_discount_usages_by_id.call(
            task_id=str(uuid.uuid4()), kwargs=kwargs,
        )

    await client.invalidate_caches()

    mocked_time.set(
        datetime.datetime.fromisoformat('2021-06-26T18:00:00+00:00'),
    )
    await client.invalidate_caches()

    request = {
        'common_conditions': {
            'request_time': request_time,
            'client_timezone': 'Europe/Moscow',
            'tariff_zone': 'moscow',
            'application_name': 'iphone',
            'user_tags': ['user_tag'],
            'has_yaplus': True,
            'waypoints': [[1.0, 2.0]],
            'user_info': {
                'user_id': 'user_id',
                'phone_id': PHONE_ID,
                'phone_hash': '138aa82720f81ba2249011d',
                'personal_phone_id': 'personal_phone_id',
                'yandex_uid': 'Yandex_uid',
            },
            'payment': {'type': 'card', 'method_id': 'card_method_id'},
            'client_supports': ['cashback'],
        },
        'subqueries': [{'tariff': 'econom', 'surge': 1.2}],
    }
    response = await client.post(
        'v3/match-discounts/', headers=common.get_headers(), json=request,
    )
    assert response.status == 200
    data = response.json()
    data.pop('discount_offer_id')
    if not should_return_discount:
        assert data == {'discounts': []}
        return
    discount = {
        'discount_id': common.START_DATA_ID,
        'discount_class': 'default',
        'discount_value': {'value': 10.0, 'value_type': 'flat'},
        'name': '1',
        'is_price_strikethrough': True,
        'active_period_end': '2021-07-08T15:00:00+00:00',
        **additional_discount_data,
    }
    expected: dict = {
        'discounts': [
            {
                'cashback_discounts': [],
                'money_discounts': [],
                'tariff': 'econom',
            },
        ],
    }
    if is_money:
        expected['discounts'][0]['money_discounts'].append(discount)
    else:
        expected['discounts'][0]['cashback_discounts'].append(discount)
    assert data == expected
    assert v1_orders.times_called <= 1
