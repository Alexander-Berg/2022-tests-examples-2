from datetime import datetime
import typing

import pytest
import pytz

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.date_time import date_time_vars
from order_notify.repositories.order_info import OrderData


STATUS_UPDATES = [
    {
        'p': {'taxi_status': 'transporting'},
        'c': datetime(2018, 12, 31, 16, 30, 00, tzinfo=pytz.UTC),
    },
    {
        'p': {'taxi_status': 'complete'},
        'c': datetime(2018, 12, 31, 17, 30, 00),
    },
]


DEFAULT_ORDER_DATA = OrderData(
    brand='yataxi',
    country='rus',
    order={'nz': 'moscow', 'statistics': {'travel_time': 2314}},
    order_proc={
        'order': {
            'request': {'due': datetime.fromisoformat('2018-12-31 22:00:00')},
        },
        'order_info': {'statistics': {'status_updates': STATUS_UPDATES}},
    },
)


@pytest.fixture(name='mock_functions')
def mock_template_vars_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.detailed_time = Counter()

    counters = Counters()

    @patch('order_notify.repositories.date_time.date_time_vars._detailed_time')
    def _detailed_time(
            context: stq_context.Context,
            seconds: typing.Optional[int],
            locale: str,
    ) -> typing.Optional[str]:
        counters.detailed_time.call()
        assert seconds == 2314
        assert locale == 'ru'
        return f'{seconds // 60} m'

    return counters


@pytest.mark.translations(
    notify={
        'helpers.month_1_part': {'ru': 'января'},
        'helpers.humanized_date_fmt': {'ru': '%(day)d %(month)s %(year)04d г'},
    },
)
async def test_get_date_time_vars(
        stq3_context: stq_context.Context,
        mock_get_cashed_zones,
        mock_functions,
):
    expected_vars = {
        'date': '1 января 2019 г',
        'finish_transporting_time': '20:30',
        'ride_time': '38 m',
        'start_transporting_time': '19:30',
    }
    date_vars = await date_time_vars.get_date_time_vars(
        context=stq3_context, order_data=DEFAULT_ORDER_DATA, locale='ru',
    )
    assert date_vars == expected_vars
