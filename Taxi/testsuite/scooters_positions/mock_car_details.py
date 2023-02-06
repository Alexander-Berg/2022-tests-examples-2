import pytest

FILENAME = 'car_details.json'


class CarDetailsContext:
    def __init__(self, scooters):
        self.scooters = scooters

    def car_details(self):
        return {'timestamp': 1511434276, 'cars': self.scooters}


@pytest.fixture(autouse=True)
def car_details(mockserver, load_json):
    scooters = []
    try:
        scooters = load_json(FILENAME)
    except FileNotFoundError:
        pass

    ctx = CarDetailsContext(scooters)

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _car_details_handler(request):
        return mockserver.make_response(json=ctx.car_details())

    return ctx
