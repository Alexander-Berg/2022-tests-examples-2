import pytest

FILENAME = 'surge_zones.json'
ERROR_MSG = f'file {FILENAME} not found'


class AdminSurgerContext:
    def __init__(self, zones):
        self.zones = {zone['id']: zone for zone in zones}

        for zone in self.zones.values():
            if 'updated' not in zone:
                zone['updated'] = '2020-09-18T07:40:00+00:00'
            for experiment in zone['forced']:
                if 'experiment_name' not in experiment:
                    experiment['experiment_name'] = '<unnamed experiment>'

    def enumerate_zones(self):
        return [
            {
                'id': zone['id'],
                'name': zone['name'],
                'geometry': zone['geometry'],
            }
            for zone in self.zones.values()
        ]

    def get_zone(self, zone_id):
        return self.zones[zone_id]


@pytest.fixture(autouse=True)
def admin_surger(mockserver, load_json):
    zones = []
    try:
        zones = load_json(FILENAME)
    except FileNotFoundError:
        pass

    ctx = AdminSurgerContext(zones)

    @mockserver.json_handler('/taxi-admin-surger/enumerate_zones/')
    def _enumerate_zones(request):
        return mockserver.make_response(json=ctx.enumerate_zones())

    @mockserver.json_handler('/taxi-admin-surger/get_zone/')
    def _get_zone(request):
        zone_id = request.query['id']
        if zone_id not in ctx.zones:
            return mockserver.make_response(
                f'Cannot find zone with id {zone_id}', status=404,
            )
        return mockserver.make_response(json=ctx.get_zone(zone_id))

    return ctx
