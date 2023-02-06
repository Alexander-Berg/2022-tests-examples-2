import pytest

MOCK_POSITION = {'lat': 55.751244, 'lon': 37.618423}


@pytest.fixture(name='driver_trackstory')
def _mock_position(mockserver):
    class Context:
        def __init__(self):
            self.mock_handler = {}
            self.position = MOCK_POSITION

        def set_position(self, pos):
            self.position = pos

    context = Context()

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_position(request):
        return {
            'position': {
                'lat': context.position['lat'],
                'lon': context.position['lon'],
                'timestamp': 1552003200,
            },
            'type': 'adjusted',
        }

    context.mock_handler = _mock_position
    return context
