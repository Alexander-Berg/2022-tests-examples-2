import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.route import route_vars


@pytest.mark.parametrize(
    'meters, expected_dist',
    [
        pytest.param(0, '10 вм', id='zero_dist'),
        pytest.param(99.9, '100 м', id='0 < dist < 100'),
        pytest.param(899.9, '900 ум', id='100 < dist <= 900'),
        pytest.param(9899.9, '9,9 км', id='900 < dist <= 9900 without zero'),
        pytest.param(9000, '9 укм', id='900 < dist <= 9900 with zero'),
        pytest.param(12345, '13 укм', id='0 < dist < 100'),
    ],
)
@pytest.mark.translations(
    tariff={
        'round.few_meters': {'ru': '10 вм'},
        'round.tens_meters': {'ru': '%(value).0f м'},
        'round.hundreds_meters': {'ru': '%(value).0f ум'},
        'round.kilometers': {'ru': '%(value).0f укм'},
        'detailed.kilometer': {'ru': 'км'},
    },
)
def test_round_distance(
        stq3_context: stq_context.Context, meters, expected_dist,
):
    dist = route_vars.round_distance(
        context=stq3_context, meters=meters, locale='ru',
    )
    assert dist == expected_dist
