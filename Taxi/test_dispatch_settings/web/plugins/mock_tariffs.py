import typing as tp

import pytest


@pytest.fixture(name='tariffs')
def _tariffs(mockserver):
    class TariffsContext:
        def __init__(self):
            self.zones = set()

        def set_zones(self, zones: tp.List[str]):
            self.zones = set(zones)

    context = TariffsContext()

    @mockserver.json_handler('/individual-tariffs/internal/v1/tariffs/summary')
    def _individual_tariffs_mock(request):
        return {
            'tariffs': [
                {
                    'id': '1',
                    'home_zone': zone,
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                }
                for zone in context.zones
            ],
        }

    return context
