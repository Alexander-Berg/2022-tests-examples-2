import pytest


@pytest.fixture(autouse=True)
def mock_parks(mockserver, db):
    @mockserver.json_handler('/parks/driver-profiles/search')
    def parks_driver_profiles_search(request):
        profiles = []
        drivers_cursor = db.dbdrivers.find()
        for driver in drivers_cursor:
            driver.pop('_id', None)
            driver['id'] = driver['driver_id']
            driver.pop('driver_id', None)
            profile = {
                'park': {'id': driver['park_id']},
                'driver': driver,
                'accounts': [
                    {
                        'id': driver['id'],
                        'type': 'current',
                        'balance': driver.get('balance', '0.0000'),
                        'currency': 'RUB',
                    },
                ],
            }
            profiles.append(profile)
        return {'profiles': profiles}
