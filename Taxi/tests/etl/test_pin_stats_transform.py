from test_helpers.common import load_test_json
from etl.processes.pin_stats.loader import PinStatsSource
from src.lib.tariff_zone_extractor.tariffs import TariffZoneData


class MapperMock:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return TariffZoneData('123', 'moscow', 'moscow', ['econom', 'uberx'])


def test_pin_stats_transform():
    raw_pins = sorted(load_test_json('raw_pins.json'), key=lambda x: x['_id'])
    expected_pins = load_test_json('expected_pins.json')

    tz_to_city = {'moscow': 'Москва'}
    tz_extractor = MapperMock()

    result_pins = \
        list(PinStatsSource(tz_extractor, tz_to_city).process_pins(raw_pins))

    # date type cannot be serialized/desearialized to/from json
    for i, pin in enumerate(result_pins):
        pin['dt'] = str(pin['dt'])

    assert result_pins == expected_pins
