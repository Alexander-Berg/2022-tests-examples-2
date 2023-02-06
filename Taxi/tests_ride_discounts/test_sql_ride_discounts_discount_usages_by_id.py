import datetime
import decimal
import uuid

import dateutil.parser
import pytest

from tests_ride_discounts import common

TIME = '2020-01-01T00:00:00+00:00'
CANCEL_TIME = '2020-01-02T00:00:00+00:00'
ORDER_ID = 'test_order_id'
PERSONAL_PHONE_ID = 'test_personal_phone_id'
CALL_DEPOSIT_ONLY_FOR_CASHBACKS = pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='ride_discounts_call_deposit_in_stq',
    consumers=['ride-discounts/ride_discounts_discount_usages_by_id'],
    clauses=[
        {
            'title': '1',
            'predicate': {'init': {}, 'type': 'true'},
            'value': {'type': 'enabled_only_for_cashbacks'},
        },
    ],
    default_value={'type': 'disabled'},
    is_config=True,
)

CALL_DEPOSIT_ONLY_FOR_DISCOUNTS = pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='ride_discounts_call_deposit_in_stq',
    consumers=['ride-discounts/ride_discounts_discount_usages_by_id'],
    clauses=[
        {
            'title': '1',
            'predicate': {'init': {}, 'type': 'true'},
            'value': {'type': 'enabled_only_for_discounts'},
        },
    ],
    default_value={'type': 'disabled'},
    is_config=True,
)


def _check_db(expected: list, service_name: str, pgsql):
    pg_cursor = pgsql[service_name].cursor()
    columns = [
        'order_id',
        'discount_group_id',
        'personal_phone_id',
        'discount_value',
        'cancelled_at',
        'created_at',
    ]
    str_columns = ','.join(columns)
    pg_cursor.execute(
        f'SELECT {str_columns} FROM {service_name}.discount_usages',
    )
    result = [dict(zip(columns, item)) for item in pg_cursor.fetchall()]
    assert result == expected


def _shift_time(time: str) -> str:
    return (
        datetime.datetime.strptime(time, common.DATETIME_FORMAT)
        + datetime.timedelta(days=1)
    ).strftime(common.DATETIME_FORMAT)


@pytest.mark.pgsql('ride_discounts', files=['match_data.sql'])
@pytest.mark.parametrize(
    'kwargs, expected',
    (
        pytest.param(
            {
                'order_id': ORDER_ID,
                'discount_id': '123',
                'personal_phone_id': PERSONAL_PHONE_ID,
                'time': TIME,
                'type': 'ADD',
                'discount_value': None,
            },
            [],
            id='discount_not_found',
        ),
        pytest.param(
            {
                'order_id': ORDER_ID,
                'discount_id': '2',
                'personal_phone_id': None,
                'time': TIME,
                'type': 'ADD',
                'discount_value': None,
            },
            [],
            id='without_personal_phone_id',
        ),
        pytest.param(
            {
                'order_id': ORDER_ID,
                'discount_id': 'invalid',
                'personal_phone_id': PERSONAL_PHONE_ID,
                'time': TIME,
                'type': 'ADD',
                'discount_value': None,
            },
            [],
            id='invalid_discount_id',
        ),
        pytest.param(
            {
                'order_id': ORDER_ID,
                'discount_id': '1',
                'personal_phone_id': PERSONAL_PHONE_ID,
                'time': TIME,
                'type': 'ADD',
                'discount_value': None,
            },
            [],
            id='without_usage_restrictions',
        ),
        pytest.param(
            {
                'order_id': ORDER_ID,
                'discount_id': '2',
                'personal_phone_id': PERSONAL_PHONE_ID,
                'time': TIME,
                'type': 'ADD',
                'discount_value': None,
            },
            [
                {
                    'created_at': dateutil.parser.parse(TIME),
                    'cancelled_at': None,
                    'discount_group_id': (
                        '22222222-2222-2222-2222-222222222222'
                    ),
                    'order_id': ORDER_ID,
                    'personal_phone_id': PERSONAL_PHONE_ID,
                    'discount_value': None,
                },
            ],
            id='with_usage_restrictions',
        ),
    ),
)
async def test_ride_discounts_discount_usages_by_id_type_add(
        stq_runner, pgsql, service_name, kwargs, expected,
):
    number_of_calls = 2
    for _ in range(number_of_calls):
        await stq_runner.ride_discounts_discount_usages_by_id.call(
            task_id=str(uuid.uuid4()), kwargs=kwargs,
        )
    _check_db(expected, service_name, pgsql)


@pytest.mark.pgsql('ride_discounts', files=['match_data.sql'])
@pytest.mark.parametrize(
    'kwargs, expected',
    (
        pytest.param(
            {
                'order_id': ORDER_ID,
                'discount_id': '1',
                'personal_phone_id': None,
                'time': TIME,
                'type': 'CANCEL',
                'discount_value': None,
            },
            [
                {
                    'created_at': dateutil.parser.parse(TIME),
                    'cancelled_at': None,
                    'discount_group_id': (
                        '22222222-2222-2222-2222-222222222222'
                    ),
                    'order_id': ORDER_ID,
                    'personal_phone_id': PERSONAL_PHONE_ID,
                    'discount_value': None,
                },
            ],
            id='without_personal_phone_id',
        ),
        pytest.param(
            {
                'order_id': ORDER_ID,
                'discount_id': '1',
                'personal_phone_id': PERSONAL_PHONE_ID,
                'time': TIME,
                'type': 'CANCEL',
                'discount_value': None,
            },
            [
                {
                    'created_at': dateutil.parser.parse(TIME),
                    'cancelled_at': None,
                    'discount_group_id': (
                        '22222222-2222-2222-2222-222222222222'
                    ),
                    'order_id': ORDER_ID,
                    'personal_phone_id': PERSONAL_PHONE_ID,
                    'discount_value': None,
                },
            ],
            id='without_usage_restrictions',
        ),
        pytest.param(
            {
                'order_id': ORDER_ID,
                'discount_id': '2',
                'personal_phone_id': PERSONAL_PHONE_ID,
                'time': CANCEL_TIME,
                'type': 'CANCEL',
                'discount_value': None,
            },
            [
                {
                    'created_at': dateutil.parser.parse(TIME),
                    'cancelled_at': dateutil.parser.parse(CANCEL_TIME),
                    'discount_group_id': (
                        '22222222-2222-2222-2222-222222222222'
                    ),
                    'order_id': ORDER_ID,
                    'personal_phone_id': PERSONAL_PHONE_ID,
                    'discount_value': None,
                },
            ],
            id='with_usage_restrictions',
        ),
    ),
)
async def test_ride_discounts_discount_usages_by_id_type_cancel(
        stq_runner, pgsql, service_name, kwargs, expected,
):
    await stq_runner.ride_discounts_discount_usages_by_id.call(
        task_id=str(uuid.uuid4()),
        kwargs={
            'order_id': ORDER_ID,
            'discount_id': '2',
            'personal_phone_id': PERSONAL_PHONE_ID,
            'time': TIME,
            'type': 'ADD',
            'discount_value': None,
        },
    )
    number_of_calls = 2
    for _ in range(number_of_calls):
        await stq_runner.ride_discounts_discount_usages_by_id.call(
            task_id=str(uuid.uuid4()), kwargs=kwargs,
        )
    _check_db(expected, service_name, pgsql)


@pytest.mark.pgsql('ride_discounts', files=['match_data.sql'])
@pytest.mark.parametrize(
    'kwargs, expected, expected_deposit_requests',
    (
        pytest.param(
            {
                'order_id': ORDER_ID,
                'discount_id': '2',
                'personal_phone_id': PERSONAL_PHONE_ID,
                'time': TIME,
                'type': 'FINISH',
                'discount_value': None,
            },
            [],
            [],
            id='without_budget_restriction',
        ),
        pytest.param(
            {
                'order_id': ORDER_ID,
                'discount_id': '1',
                'personal_phone_id': None,
                'time': TIME,
                'type': 'FINISH',
                'discount_value': None,
            },
            [],
            [],
            id='without_personal_phone_id',
        ),
        pytest.param(
            {
                'order_id': ORDER_ID,
                'discount_id': '1',
                'personal_phone_id': PERSONAL_PHONE_ID,
                'time': TIME,
                'type': 'FINISH',
                'discount_value': -10.11,
            },
            [
                {
                    'created_at': dateutil.parser.parse(TIME),
                    'cancelled_at': None,
                    'discount_group_id': (
                        '11111111-1111-1111-1111-111111111111'
                    ),
                    'order_id': ORDER_ID,
                    'personal_phone_id': PERSONAL_PHONE_ID,
                    'discount_value': decimal.Decimal('10.11'),
                },
            ],
            [],
            id='with_budget_restriction_negative',
        ),
        pytest.param(
            {
                'order_id': ORDER_ID,
                'discount_id': '1',
                'personal_phone_id': PERSONAL_PHONE_ID,
                'time': TIME,
                'type': 'FINISH',
                'discount_value': 10.11,
            },
            [
                {
                    'created_at': dateutil.parser.parse(TIME),
                    'cancelled_at': None,
                    'discount_group_id': (
                        '11111111-1111-1111-1111-111111111111'
                    ),
                    'order_id': ORDER_ID,
                    'personal_phone_id': PERSONAL_PHONE_ID,
                    'discount_value': decimal.Decimal('10.11'),
                },
            ],
            [],
            id='with_budget_restriction',
        ),
        pytest.param(
            {
                'order_id': ORDER_ID,
                'discount_id': '1',
                'personal_phone_id': PERSONAL_PHONE_ID,
                'time': TIME,
                'type': 'FINISH',
                'discount_value': 10.11,
                'currency': 'RUB',
            },
            [
                {
                    'created_at': dateutil.parser.parse(TIME),
                    'cancelled_at': None,
                    'discount_group_id': (
                        '11111111-1111-1111-1111-111111111111'
                    ),
                    'order_id': ORDER_ID,
                    'personal_phone_id': PERSONAL_PHONE_ID,
                    'discount_value': decimal.Decimal('10.11'),
                },
            ],
            [
                {
                    'amount': '10.110000',
                    'currency': 'RUB',
                    'event_at': '2020-01-01T00:00:00+0000',
                    'limit_ref': 'discount_with_maximum_budget_per_person',
                },
                {
                    'amount': '10.110000',
                    'currency': 'RUB',
                    'event_at': '2020-01-01T00:00:00+0000',
                    'limit_ref': 'discount_with_maximum_budget_per_person',
                },
            ],
            marks=CALL_DEPOSIT_ONLY_FOR_CASHBACKS,
            id='cashback_with_currency',
        ),
        pytest.param(
            {
                'order_id': ORDER_ID,
                'discount_id': '3',
                'personal_phone_id': PERSONAL_PHONE_ID,
                'time': TIME,
                'type': 'FINISH',
                'discount_value': 10.11,
                'currency': 'RUB',
            },
            [],
            [],
            marks=CALL_DEPOSIT_ONLY_FOR_CASHBACKS,
            id='money_with_currency_exp_disabled',
        ),
        pytest.param(
            {
                'order_id': ORDER_ID,
                'discount_id': '3',
                'personal_phone_id': PERSONAL_PHONE_ID,
                'time': TIME,
                'type': 'FINISH',
                'discount_value': 10.11,
                'currency': 'RUB',
            },
            [],
            [
                {
                    'amount': '10.110000',
                    'currency': 'RUB',
                    'event_at': '2020-01-01T00:00:00+0000',
                    'limit_ref': 'discount_without_any_restrictions',
                },
                {
                    'amount': '10.110000',
                    'currency': 'RUB',
                    'event_at': '2020-01-01T00:00:00+0000',
                    'limit_ref': 'discount_without_any_restrictions',
                },
            ],
            marks=CALL_DEPOSIT_ONLY_FOR_DISCOUNTS,
            id='money_with_currency',
        ),
    ),
)
async def test_ride_discounts_discount_usages_by_id_type_finish(
        stq_runner,
        pgsql,
        service_name,
        kwargs,
        expected,
        mockserver,
        expected_deposit_requests,
):
    deposit_requests = []

    @mockserver.json_handler('/billing-limits/v1/deposit')
    def _deposit_handler(request):
        deposit_requests.append(request.json)
        return {}

    number_of_calls = 2
    for _ in range(number_of_calls):
        await stq_runner.ride_discounts_discount_usages_by_id.call(
            task_id=str(uuid.uuid4()), kwargs=kwargs,
        )
    _check_db(expected, service_name, pgsql)
    assert deposit_requests == expected_deposit_requests


@pytest.mark.pgsql('ride_discounts', files=['match_data.sql'])
@pytest.mark.parametrize(
    'kwargs, expected',
    (
        pytest.param(
            {
                'order_id': ORDER_ID,
                'discount_id': '2',
                'personal_phone_id': PERSONAL_PHONE_ID,
                'time': CANCEL_TIME,
                'type': 'FINISH',
            },
            [
                {
                    'created_at': dateutil.parser.parse(TIME),
                    'cancelled_at': dateutil.parser.parse(CANCEL_TIME),
                    'discount_group_id': (
                        '22222222-2222-2222-2222-222222222222'
                    ),
                    'order_id': ORDER_ID,
                    'personal_phone_id': PERSONAL_PHONE_ID,
                    'discount_value': None,
                },
            ],
            id='without_discount_value',
        ),
        pytest.param(
            {
                'order_id': ORDER_ID,
                'discount_id': '2',
                'personal_phone_id': PERSONAL_PHONE_ID,
                'time': CANCEL_TIME,
                'type': 'FINISH',
                'discount_value': 0.0,
            },
            [
                {
                    'created_at': dateutil.parser.parse(TIME),
                    'cancelled_at': dateutil.parser.parse(CANCEL_TIME),
                    'discount_group_id': (
                        '22222222-2222-2222-2222-222222222222'
                    ),
                    'order_id': ORDER_ID,
                    'personal_phone_id': PERSONAL_PHONE_ID,
                    'discount_value': None,
                },
            ],
            id='with_zero_discount_value',
        ),
    ),
)
async def test_ride_discounts_discount_usages_by_id_finish_without_value(
        stq_runner, pgsql, service_name, kwargs, expected,
):
    await stq_runner.ride_discounts_discount_usages_by_id.call(
        task_id=str(uuid.uuid4()),
        kwargs={
            'order_id': ORDER_ID,
            'discount_id': '2',
            'personal_phone_id': PERSONAL_PHONE_ID,
            'time': TIME,
            'type': 'ADD',
            'discount_value': None,
        },
    )
    number_of_calls = 2
    for _ in range(number_of_calls):
        await stq_runner.ride_discounts_discount_usages_by_id.call(
            task_id=str(uuid.uuid4()), kwargs=kwargs,
        )
    _check_db(expected, service_name, pgsql)
