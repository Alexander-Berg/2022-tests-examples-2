import pytest

FILENAME = 'scooters_areas.json'


class ScootersAreasContext:
    def __init__(self, areas):
        self.areas = areas

    def scooters_areas(self):
        return {'areas': self.areas}


@pytest.fixture(autouse=True)
def scooters_misc_areas_mock(mockserver, load_json):
    areas = []
    try:
        areas = load_json(FILENAME)
    except FileNotFoundError:
        pass

    ctx = ScootersAreasContext(areas)

    @mockserver.json_handler('/scooters-misc/scooters-misc/v1/areas')
    def _scooters_misc_areas_handler(request):
        return mockserver.make_response(json=ctx.scooters_areas())

    return ctx
