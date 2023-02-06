import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.date_time import date_time_vars


@pytest.mark.parametrize(
    'seconds, expected_time',
    [
        pytest.param(None, None, id='None seconds'),
        pytest.param(3601, '1 ч', id='1 hour 1 sec'),
        pytest.param(3661, '1 ч 1 мин', id='1 hour 1 min 1 sec'),
        pytest.param(301, '5 мин', id='5 min 1 sec'),
        pytest.param(60, '1 мин', id='1 min 0 sec'),
        pytest.param(61, '1 мин 1 сек', id='1 min 1 sec'),
        pytest.param(59, '59 сек', id='59 sec'),
        pytest.param(0, '0 сек', id='0 sec'),
    ],
)
@pytest.mark.translations(
    tariff={
        'detailed.hours': {'ru': '%(value).0f ч'},
        'detailed.minutes': {'ru': '%(value).0f мин'},
        'detailed.seconds': {'ru': '%(value).0f сек'},
    },
)
def test_detailed_time(
        stq3_context: stq_context.Context, seconds, expected_time,
):
    detailed_t = date_time_vars._detailed_time(  # pylint: disable=W0212
        context=stq3_context, seconds=seconds, locale='ru',
    )
    assert detailed_t == expected_time
