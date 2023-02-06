import geojson
from libstall.point import Point


def test_point(tap):
    with tap.plan(4):
        point = Point({
            'lat':    55,
            'lon':    '37',
        })
        tap.ok(point, 'Точка')
        tap.eq(point.lat, 55, 'lat')
        tap.eq(point.lon, 37, 'lon')

        tap.eq(
            point.pure_sql(),
            "'(37.0,55.0)'",
            'Сереализация SQL'
        )


def test_geojson(tap):
    with tap.plan(3):
        point = Point(geojson.Point((37, 55)))
        tap.ok(point, 'Точка')

        serialized = point.pure_python()
        tap.eq(
            serialized,
            {
                "geometry": {"coordinates": [37.0, 55.0], "type": "Point"},
                "properties": {},
                "type": "Feature",
            },
            'Сереализация GeoJSON'
        )

        deserialized = Point(serialized)
        tap.eq(point, deserialized, 'Десериализация из GeoJSON')


def test_init(tap):
    with tap.plan(6):
        point = Point((60.001892, 30.260609))
        tap.eq(point.lat, 60.001892, 'lat')
        tap.eq(point.lon, 30.260609, 'lon')

        point = Point(geojson.Point((30.260609, 60.001892)))
        tap.eq(point.lat, 60.001892, 'lat')
        tap.eq(point.lon, 30.260609, 'lon')

        point = Point({'lat': 61.560511, 'lon': 22.769105})
        tap.eq(point.lat, 61.560511, 'lat')
        tap.eq(point.lon, 22.769105, 'lon')


def test_distance(tap):
    with tap.plan(3):
        point1 = Point((60.001892, 30.260609))

        point2 = Point(geojson.Point((30.260609, 60.001892)))
        tap.eq(point1.distance(point2), 0, 'Идентичные координаты')

        point2 = [60.002490, 30.258593]
        tap.eq(int(point1.distance(point2)), 130, 'Южнее и восточнее')

        point2 = {'lat': 61.560511, 'lon': 22.769105}
        tap.eq(int(point1.distance(point2)), 441826, 'Севернее и западнее')
