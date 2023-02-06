import datetime as dt
import decimal

import pytest

from fleet_rent.entities import park as park_entities
from fleet_rent.entities import rent as rent_entities
from fleet_rent.generated.web import web_context as context_module
from fleet_rent.services import billing_reports
from fleet_rent.use_cases.driver_expenses import by_park
from fleet_rent.use_cases.driver_expenses import by_period
from fleet_rent.use_cases.driver_expenses import errors

parse_time = dt.datetime.fromisoformat  # pylint: disable=invalid-name


@pytest.fixture
def _mock_load_parks_batch(patch):
    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info_batch')
    async def _get_batch(park_ids):
        assert park_ids == {'park_id1', 'park_id2'}
        parks = [
            park_entities.Park(id='park_id1', clid='clid1'),
            park_entities.Park(id='park_id2', clid='clid2'),
        ]
        return {x.id: x for x in parks}


@pytest.fixture
def _mock_withdraw_balances_sums(patch):
    @patch(
        'fleet_rent.services.billing_reports.'
        'BillingReportsService.get_withdraw_balances_sums',
    )
    async def _mock_withdraw_balances_sums(parks_currencies, rents, times):
        return {
            (
                'park_id1',
                parse_time('2020-01-01T16:00+00:00'),
            ): decimal.Decimal(10),
            (
                'park_id2',
                parse_time('2020-01-01T16:00+00:00'),
            ): decimal.Decimal(5),
            (
                'park_id1',
                parse_time('2020-01-01T17:00+00:00'),
            ): decimal.Decimal(13),
            (
                'park_id2',
                parse_time('2020-01-01T17:00+00:00'),
            ): decimal.Decimal(13),
            (
                'park_id1',
                parse_time('2020-01-02T17:00+00:00'),
            ): decimal.Decimal(20),
            (
                'park_id2',
                parse_time('2020-01-02T17:00+00:00'),
            ): decimal.Decimal(30),
        }


@pytest.mark.pgsql('fleet_rent', files=['base_case.sql'])
async def test_ok_by_period(
        web_context: context_module.Context,
        patch,
        mock_load_park_info,
        _mock_withdraw_balances_sums,
):
    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_independent_driver_currency',
    )
    async def _get_currency(*args, **kwargs):
        return 'RUB'

    result = await web_context.use_cases.driver_expenses.by_period(
        'driver_park_id',
        'driver_id',
        [
            (
                parse_time('2020-01-01T16:00+00:00'),
                parse_time('2020-01-01T17:00+00:00'),
            ),
            (
                parse_time('2020-01-01T17:00+00:00'),
                parse_time('2020-01-02T17:00+00:00'),
            ),
        ],
    )
    assert result
    assert result.currency == 'RUB'
    expenses = list(result.expenses)

    utc = dt.timezone.utc
    assert expenses == [
        by_period.Expense(
            begin_time=dt.datetime(2020, 1, 1, 16, 0, tzinfo=utc),
            end_time=dt.datetime(2020, 1, 1, 17, 0, tzinfo=utc),
            amount=decimal.Decimal('11'),
        ),
        by_period.Expense(
            begin_time=dt.datetime(2020, 1, 1, 17, 0, tzinfo=utc),
            end_time=dt.datetime(2020, 1, 2, 17, 0, tzinfo=utc),
            amount=decimal.Decimal('24'),
        ),
    ]


async def test_non_independent_by_period(
        web_context: context_module.Context, mock_load_park_info,
):
    use_case = web_context.use_cases.driver_expenses
    with pytest.raises(errors.NonSingleDriverPark):
        await use_case.by_period(
            'park_id',
            'driver_id',
            [
                (
                    parse_time('2020-01-01T16:00+00:00'),
                    parse_time('2020-01-01T17:00+00:00'),
                ),
                (
                    parse_time('2020-01-01T17:00+00:00'),
                    parse_time('2020-01-02T17:00+00:00'),
                ),
            ],
        )


async def test_invalid_times_by_period(
        web_context: context_module.Context, mock_load_park_info,
):
    use_case = web_context.use_cases.driver_expenses
    times = [
        (
            parse_time('2020-01-01T16:00+00:00'),
            parse_time('2020-01-01T16:14+00:00'),
        ),
        (
            parse_time('2020-01-01T16:00:01+00:00'),
            parse_time('2020-01-01T17:00+00:00'),
        ),
    ]
    for pair in times:
        with pytest.raises(errors.InvalidTimePrecision):
            await use_case.by_period('driver_park_id', 'driver_id', [pair])


async def test_invalid_periods_by_period(
        web_context: context_module.Context, mock_load_park_info,
):
    use_case = web_context.use_cases.driver_expenses
    with pytest.raises(errors.InvalidTimeRange):
        await use_case.by_period(
            'driver_park_id',
            'driver_id',
            [
                (
                    parse_time('2020-01-01T17:00+00:00'),
                    parse_time('2020-01-01T16:00+00:00'),
                ),
            ],
        )


@pytest.mark.pgsql('fleet_rent', files=['base_case.sql'])
async def test_ok_by_park(
        web_context: context_module.Context,
        mock_load_park_info,
        patch,
        _mock_withdraw_balances_sums,
        _mock_load_parks_batch,
):
    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_independent_driver_currency',
    )
    async def _get_currency(*args, **kwargs):
        return 'RUB'

    use_case = web_context.use_cases.driver_expenses
    result = await use_case.by_park(
        'driver_park_id',
        'driver_id',
        parse_time('2020-01-01T16:00+00:00'),
        parse_time('2020-01-01T17:00+00:00'),
    )
    assert result.currency == 'RUB'

    assert list(result.expenses) == [
        by_park.ParkExpense(
            park=park_entities.Park(id='park_id1', clid='clid1'),
            amount=decimal.Decimal(3),
        ),
        by_park.ParkExpense(
            park=park_entities.Park(id='park_id2', clid='clid2'),
            amount=decimal.Decimal(8),
        ),
    ]


async def test_non_independent_by_park(
        web_context: context_module.Context, mock_load_park_info,
):
    use_case = web_context.use_cases.driver_expenses
    with pytest.raises(errors.NonSingleDriverPark):
        await use_case.by_park(
            'park_id',
            'driver_id',
            parse_time('2020-01-01T16:00+00:00'),
            parse_time('2020-01-01T17:00+00:00'),
        )


async def test_invalid_times_by_park(web_context: context_module.Context):
    use_case = web_context.use_cases.driver_expenses

    times = [
        (
            parse_time('2020-01-01T16:00+00:00'),
            parse_time('2020-01-01T16:14+00:00'),
        ),
        (
            parse_time('2020-01-01T16:00:01+00:00'),
            parse_time('2020-01-01T17:00+00:00'),
        ),
    ]
    for pair in times:
        with pytest.raises(errors.InvalidTimePrecision):
            await use_case.by_park('driver_park_id', 'driver_id', *pair)


async def test_invalid_periods_by_park(web_context: context_module.Context):
    use_case = web_context.use_cases.driver_expenses

    with pytest.raises(errors.InvalidTimeRange):
        await use_case.by_park(
            'driver_park_id',
            'driver_id',
            parse_time('2020-01-01T17:00+00:00'),
            parse_time('2020-01-01T16:00+00:00'),
        )


@pytest.mark.pgsql('fleet_rent', files=['base_case_in_park.sql'])
async def test_ok_in_park(
        web_context: context_module.Context,
        mock_load_park_info,
        mock_load_car_info,
        patch,
        _mock_withdraw_balances_sums,
):
    from fleet_rent.use_cases.driver_expenses import in_park

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_independent_driver_currency',
    )
    async def _get_currency(*args, **kwargs):
        return 'RUB'

    @patch(
        'fleet_rent.services.billing_reports.'
        'BillingReportsService.driver_expenses_by_rent',
    )
    async def _get_expenses(*args, **kwargs):
        return {
            rent_entities.OwnerKey('park_id1', 1): [
                billing_reports.Expense(
                    decimal.Decimal(10),
                    dt.datetime(2020, 1, 2, tzinfo=dt.timezone.utc),
                ),
                billing_reports.Expense(
                    decimal.Decimal(20),
                    dt.datetime(2020, 1, 3, tzinfo=dt.timezone.utc),
                ),
            ],
            rent_entities.OwnerKey('park_id1', 2): [
                billing_reports.Expense(
                    decimal.Decimal(30),
                    dt.datetime(2020, 1, 4, tzinfo=dt.timezone.utc),
                ),
            ],
        }

    use_case = web_context.use_cases.driver_expenses
    result = await use_case.in_park(
        'park_id1',
        'driver_park_id',
        'driver_id',
        parse_time('2020-01-01T16:00+00:00'),
        parse_time('2020-01-01T17:00+00:00'),
    )
    assert result.currency == 'RUB'
    assert result.owner_park.id == 'park_id1'
    expenses = list(result.expenses)
    assert expenses[0].rent_data.rent.record_id == 'record_id1'
    assert expenses[0].rent_data.car_info.id == 'car_id1'
    assert tuple(expenses[0].expenses) == (
        in_park.Expense(
            dt.datetime(2020, 1, 2, tzinfo=dt.timezone.utc),
            decimal.Decimal(10),
        ),
        in_park.Expense(
            dt.datetime(2020, 1, 3, tzinfo=dt.timezone.utc),
            decimal.Decimal(20),
        ),
    )
    assert expenses[1].rent_data.rent.record_id == 'record_id2'
    assert tuple(expenses[1].expenses) == (
        in_park.Expense(
            dt.datetime(2020, 1, 4, tzinfo=dt.timezone.utc),
            decimal.Decimal(30),
        ),
    )


async def test_non_independent_in_park(
        web_context: context_module.Context, mock_load_park_info,
):
    use_case = web_context.use_cases.driver_expenses
    with pytest.raises(errors.NonSingleDriverPark):
        await use_case.in_park(
            'park_id1',
            'park_id2',
            'driver_id',
            parse_time('2020-01-01T16:00+00:00'),
            parse_time('2020-01-01T17:00+00:00'),
        )


async def test_invalid_times_in_park(web_context: context_module.Context):
    use_case = web_context.use_cases.driver_expenses

    times = [
        (
            parse_time('2020-01-01T16:00+00:00'),
            parse_time('2020-01-01T16:14+00:00'),
        ),
        (
            parse_time('2020-01-01T16:00:01+00:00'),
            parse_time('2020-01-01T17:00+00:00'),
        ),
    ]
    for pair in times:
        with pytest.raises(errors.InvalidTimePrecision):
            await use_case.in_park(
                'park_id', 'driver_park_id', 'driver_id', *pair,
            )


async def test_invalid_periods_in_park(web_context: context_module.Context):
    use_case = web_context.use_cases.driver_expenses

    with pytest.raises(errors.InvalidTimeRange):
        await use_case.in_park(
            'park_id',
            'driver_park_id',
            'driver_id',
            parse_time('2020-01-01T17:00+00:00'),
            parse_time('2020-01-01T16:00+00:00'),
        )
