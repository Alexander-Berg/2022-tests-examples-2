import pytest


@pytest.fixture(name='driver_trackstory')
def mock_grocery_supply(mockserver):
    class Context:
        def __init__(self):
            self.drivers = {}

        def set_position(
                self,
                driver_id: str,
                direction: int = 0,
                lat: float = 0.0,
                lon: float = 0.0,
                speed: float = 0.0,
                timestamp: int = 0,
        ):
            self.drivers[driver_id] = {
                'direction': direction,
                'lat': lat,
                'lon': lon,
                'speed': speed,
                'timestamp': timestamp,
            }

    context = Context()

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        driver_id = request.json['driver_id']
        position = (
            context.drivers[driver_id]
            if driver_id in context.drivers
            else {
                'direction': 0,
                'lat': 0.0,
                'lon': 0.0,
                'speed': 0.0,
                'timestamp': 0,
            }
        )

        return mockserver.make_response(
            json={'position': position, 'type': 'raw'}, status=200,
        )

    return context
