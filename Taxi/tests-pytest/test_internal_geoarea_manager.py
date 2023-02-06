import datetime

from taxi.internal import geoarea_manager
from taxi.internal.dbh import geoareas


def test_polygon():
    geoarea = geoareas.Doc({
        'area': 1,
        'created': datetime.datetime.utcnow(),
        'geometry': {
            'type': 'Polygon',
            'coordinates': [
                [[0, 0], [0, 1], [1, 1], [1, 0]]
            ]
        },
        'name': 'geoarea1',
        'removed': False
    })

    polygon = geoarea_manager.Polygon.from_geoarea(geoarea)
    assert polygon.contains((0.5, 0.5))
    assert not polygon.contains((5, 5))
