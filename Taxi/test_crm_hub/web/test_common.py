import pytest

from crm_hub.logic import common


@pytest.mark.parametrize(
    'days_count, time_until, start_date, end_date',
    [
        (1, '13:00', '2021-03-01T00:00:00', '2021-03-01T13:00:00'),
        (2, '23:59', '2021-03-01T00:00:00', '2021-03-02T23:59:00'),
        (10, '16:09', '2021-03-01T00:00:00', '2021-03-10T16:09:00'),
    ],
)
@pytest.mark.now('2021-03-01 10:00:00')
async def test_get_dates_range(days_count, time_until, start_date, end_date):
    _start_date, _end_date = common.get_dates_range(days_count, time_until)
    assert _start_date.isoformat() == start_date
    assert _end_date.isoformat() == end_date
