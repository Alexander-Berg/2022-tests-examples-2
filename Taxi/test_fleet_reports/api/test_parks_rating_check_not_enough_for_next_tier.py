import pytest

from fleet_reports.generated.service.swagger.models import api
from fleet_reports.api.parks_rating_status import (  # noqa pylint: disable = C5521
    _check_not_enough_for_next_tier,
)


@pytest.mark.parametrize(
    'db_park,result',
    [
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29h',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 55,
                'tier': 'gold',
                'is_blacklist': False,
            },
            None,
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29h',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 55,
                'tier': 'gold',
                'is_blacklist': True,
            },
            api.NotEnoughForNextTier(reason='blacklist'),
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29h',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 55,
                'tier': 'silver',
                'is_blacklist': True,
            },
            api.NotEnoughForNextTier(reason='blacklist'),
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29h',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 55,
                'tier': 'silver',
                'next_tier_diff_points': 0.1,
                'is_blacklist': False,
                'is_cars_gold_lack': True,
                'total_cars': 10,
                'total_cars_gold_threshold': 40,
            },
            api.NotEnoughForNextTier(reason='cars', lack=30),
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29h',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 55,
                'tier': 'silver',
                'next_tier_diff_points': 1.1,
                'is_blacklist': False,
                'is_cars_gold_lack': True,
                'total_cars': 10,
                'total_cars_gold_threshold': 40,
            },
            api.NotEnoughForNextTier(reason='points', lack=1),
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29h',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 55,
                'tier': 'bronze',
                'next_tier_diff_points': 0,
                'is_blacklist': False,
                'is_cars_gold_lack': True,
                'total_cars': 10,
                'total_cars_gold_threshold': 40,
            },
            api.NotEnoughForNextTier(reason='points', lack=0),
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29h',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 55,
                'tier': 'silver',
                'next_tier_diff_points': 13.76,
                'is_blacklist': None,
                'is_cars_gold_lack': None,
                'total_cars': None,
                'total_cars_gold_threshold': None,
            },
            api.NotEnoughForNextTier(reason='points', lack=13),
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29h',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 55,
                'tier': 'weak',
                'next_tier_diff_points': 13.76,
                'is_blacklist': None,
            },
            api.NotEnoughForNextTier(reason='points', lack=13),
        ),
    ],
)
def test_check_not_enough_for_next_tier(db_park, result):
    func_result = _check_not_enough_for_next_tier(db_park)
    if isinstance(result, api.NotEnoughForNextTier):
        assert func_result.reason == result.reason
        if result.reason != 'blacklist':
            assert func_result.lack == result.lack
    else:
        assert func_result is None
