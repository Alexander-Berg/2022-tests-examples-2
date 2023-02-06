import pytest

FILENAME = 'surge_points.json'


class AdminSurgerPointsContext:
    def __init__(self, points):
        self.points = points

    def v1_point_employ(self, snapshot):
        return {
            'items': [
                {
                    'id': point['id'],
                    'position_id': point['id'],
                    'version': point['version'],
                    'created': point['created'],
                    'updated': point['updated'],
                    'location': point['location'],
                    'mode': point['mode'],
                    'name': point['name'],
                    'surge_zone_name': point['surge_zone_name'],
                    'tags': point['tags'],
                    'snapshot': point['snapshot'],
                    'employed': True,
                    'polygon': (
                        point['polygon'] if 'polygon' in point else None
                    ),
                }
                for point in self.points
                if point['snapshot'] == snapshot
            ],
        }


@pytest.fixture(autouse=True)
def admin_surger_points(mockserver, load_json):
    points = []
    try:
        points = load_json(FILENAME)
    except FileNotFoundError:
        pass

    ctx = AdminSurgerPointsContext(points)

    @mockserver.json_handler('/taxi-admin-surger/admin/v1/point/employ')
    def _point_employ(request):
        return mockserver.make_response(
            json=ctx.v1_point_employ(request.query['snapshot']),
        )

    return ctx
