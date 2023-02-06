import datetime as dt
import decimal

from fleet_rent.use_cases.driver_expenses import by_period


async def test_ok(patch, web_app_client):
    @patch(
        'fleet_rent.use_cases.driver_expenses.by_period.'
        'DriverExpensesByPeriod.__call__',
    )
    async def _impl(driver_park_id, driver_id, begin_end_pairs):
        beg1 = dt.datetime.fromisoformat('2020-01-01T00:00+00:00')
        end1 = dt.datetime.fromisoformat('2020-01-01T06:00+00:00')
        beg2 = dt.datetime.fromisoformat('2020-01-02T00:00+00:00')
        end2 = dt.datetime.fromisoformat('2020-01-06T00:00+00:00')
        assert list(begin_end_pairs) == [(beg1, end1), (beg2, end2)]
        assert driver_park_id == 'smz_park'
        assert driver_id == 'smz_did'
        res = [
            by_period.Expense(
                begin_time=beg1, end_time=end1, amount=decimal.Decimal('333'),
            ),
            by_period.Expense(
                begin_time=beg2, end_time=end2, amount=decimal.Decimal('444'),
            ),
        ]
        return by_period.Result(currency='RUB', expenses=res)

    response = await web_app_client.post(
        '/fleet-rent/v1/sys/driver-expenses/totals'
        '?driver_profile_id=smz_did&park_id=smz_park',
        json={
            'periods': [
                {
                    'begin_time': '2020-01-01T00:00',
                    'end_time': '2020-01-01T06:00',
                },
                {
                    'begin_time': '2020-01-02T00:00',
                    'end_time': '2020-01-06T00:00',
                },
            ],
        },
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert body == {
        'expenses': [
            {
                'begin_time': '2020-01-01T03:00:00+03:00',
                'end_time': '2020-01-01T09:00:00+03:00',
                'value': {'amount': '333', 'currency': 'RUB'},
            },
            {
                'begin_time': '2020-01-02T03:00:00+03:00',
                'end_time': '2020-01-06T03:00:00+03:00',
                'value': {'amount': '444', 'currency': 'RUB'},
            },
        ],
    }


async def test_no_smz(patch, web_app_client):
    @patch(
        'fleet_rent.use_cases.driver_expenses.by_period.'
        'DriverExpensesByPeriod.__call__',
    )
    async def _impl(driver_park_id, driver_id, begin_end_pairs):
        raise by_period.errors.NonSingleDriverPark()

    response = await web_app_client.post(
        '/fleet-rent/v1/sys/driver-expenses/totals'
        '?driver_profile_id=smz_did&park_id=smz_park',
        json={
            'periods': [
                {
                    'begin_time': '2020-01-01T00:00',
                    'end_time': '2020-01-01T06:00',
                },
                {
                    'begin_time': '2020-01-02T00:00',
                    'end_time': '2020-01-06T00:00',
                },
            ],
        },
    )
    assert response.status == 400, await response.text()
    body = await response.json()
    assert body['code'] == 'NOT_SINGLE_DRIVER_PARK'


async def test_invalid_times(patch, web_app_client):
    @patch(
        'fleet_rent.use_cases.driver_expenses.by_period.'
        'DriverExpensesByPeriod.__call__',
    )
    async def _impl(driver_park_id, driver_id, begin_end_pairs):
        raise by_period.errors.InvalidTimePrecision()

    response = await web_app_client.post(
        '/fleet-rent/v1/sys/driver-expenses/totals'
        '?driver_profile_id=smz_did&park_id=smz_park',
        json={
            'periods': [
                {
                    'begin_time': '2020-01-01T00:00',
                    'end_time': '2020-01-01T06:00',
                },
                {
                    'begin_time': '2020-01-02T00:00',
                    'end_time': '2020-01-06T00:00',
                },
            ],
        },
    )
    assert response.status == 400, await response.text()
    body = await response.json()
    assert body['code'] == 'INVALID_TIME_PRECISION'


async def test_invalid_ranges(patch, web_app_client):
    @patch(
        'fleet_rent.use_cases.driver_expenses.by_period.'
        'DriverExpensesByPeriod.__call__',
    )
    async def _impl(driver_park_id, driver_id, begin_end_pairs):
        raise by_period.errors.InvalidTimeRange()

    response = await web_app_client.post(
        '/fleet-rent/v1/sys/driver-expenses/totals'
        '?driver_profile_id=smz_did&park_id=smz_park',
        json={
            'periods': [
                {
                    'begin_time': '2020-01-01T00:00',
                    'end_time': '2020-01-01T06:00',
                },
                {
                    'begin_time': '2020-01-02T00:00',
                    'end_time': '2020-01-06T00:00',
                },
            ],
        },
    )
    assert response.status == 400, await response.text()
    body = await response.json()
    assert body['code'] == 'INVALID_TIME_RANGE'


async def test_non_handleable(patch, web_app_client):
    @patch(
        'fleet_rent.use_cases.driver_expenses.by_period.'
        'DriverExpensesByPeriod.__call__',
    )
    async def _impl(driver_park_id, driver_id, begin_end_pairs):
        raise by_period.errors.NonHandleableError()

    response = await web_app_client.post(
        '/fleet-rent/v1/sys/driver-expenses/totals'
        '?driver_profile_id=smz_did&park_id=smz_park',
        json={
            'periods': [
                {
                    'begin_time': '2020-01-01T00:00',
                    'end_time': '2020-01-01T06:00',
                },
                {
                    'begin_time': '2020-01-02T00:00',
                    'end_time': '2020-01-06T00:00',
                },
            ],
        },
    )
    assert response.status == 500, await response.text()
