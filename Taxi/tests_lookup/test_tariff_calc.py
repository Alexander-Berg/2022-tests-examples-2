import datetime

import pytest

from tests_lookup import lookup_params
from tests_lookup import mock_candidates


async def test_countries_weekends(
        acquire_candidate, mockserver, mocked_time, load_json,
):
    @mockserver.json_handler('/territories/v1/countries/list')
    def _mock_countries_list(request):
        request.get_data()
        return load_json('countries.json')

    order = lookup_params.create_params(tariffs=['econom'])
    order['order']['city'] = '\u041c\u043e\u0441\u043a\u0432\u0430'

    # monday (set weekend)
    now_time = datetime.datetime(2021, 3, 15, 12, tzinfo=datetime.timezone.utc)
    mocked_time.set(now_time)

    candidate = await acquire_candidate(order)
    assert candidate['ci'] == 'weekend'

    for day in range(1, 7):
        now_time = datetime.datetime(
            2021, 3, 15 + day, 12, tzinfo=datetime.timezone.utc,
        )
        mocked_time.set(now_time)

        candidate = await acquire_candidate(order)
        assert candidate['ci'] == 'workday'


@pytest.mark.config(
    LOOKUP_FEATURE_SWITCHES={'paid_supply_prioritized_in_multi_class': True},
)
async def test_paid_supply(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        result = {
            'candidates': mock_candidates.make_candidates()['candidates'][0:1],
        }
        result['candidates'][0]['classes'] = ['econom', 'business', 'vip']
        return result

    order = lookup_params.create_params(tariffs=['econom', 'business', 'vip'])
    order['extra_data'] = {
        'multiclass': {'paid_supply_classes': ['econom', 'business']},
    }
    order['order']['nz'] = 'spb'

    candidate = await acquire_candidate(order)
    assert candidate['tariff_class'] == 'business'
