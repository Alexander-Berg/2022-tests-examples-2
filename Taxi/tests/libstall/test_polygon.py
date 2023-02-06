import pytest

import geojson
from libstall.polygon import MultiPolygon, Polygon


def test_polygon(tap):
    with tap.plan(2):
        with pytest.raises(ValueError):
            Polygon([
                {'lat': 55, 'lon': 37},
                {'lat': 55, 'lon': 38},
                {'lat': 56, 'lon': 38},
                {'lat': 56, 'lon': 37},
            ])

        polygon = Polygon([
            {'lat': 55, 'lon': 37},
            {'lat': 55, 'lon': 38},
            {'lat': 56, 'lon': 38},
            {'lat': 56, 'lon': 37},
            {'lat': 55, 'lon': 37},
        ])
        tap.ok(polygon, 'Полигон')

        tap.eq(
            polygon.pure_sql(),
            "'((37.0,55.0),(38.0,55.0),(38.0,56.0),(37.0,56.0),(37.0,55.0))'",
            'Сереализация SQL'
        )


def test_geojson(tap):
    with tap.plan(3):
        with pytest.raises(ValueError):
            Polygon(geojson.Polygon([
                [
                    [37.0, 55.0],
                    [38.0, 55.0],
                    [38.0, 56.0],
                    [37.0, 56.0],
                ],
            ]))
        polygon = Polygon(geojson.Polygon([
            [
                [37.0, 55.0],
                [38.0, 55.0],
                [38.0, 56.0],
                [37.0, 56.0],
                [37.0, 55.0],
            ],
        ]))
        tap.ok(polygon, 'Полигон')

        serialized = polygon.pure_python()
        tap.eq(
            serialized,
            {
                "geometry": {
                    "coordinates": [
                        [
                            [37.0, 55.0],
                            [38.0, 55.0],
                            [38.0, 56.0],
                            [37.0, 56.0],
                            [37.0, 55.0],
                        ],
                    ],
                    "type": "Polygon"
                },
                "properties": {},
                "type": "Feature",
            },
            'Сереализация GeoJSON'
        )

        deserialized = Polygon(serialized)
        tap.eq(polygon, deserialized, 'Десериализация из GeoJSON')


def test_multipolygon(tap):
    with tap.plan(3):
        with pytest.raises(ValueError):
            MultiPolygon(geojson.MultiPolygon([
                [
                    [
                        [37.0, 55.0],
                        [38.0, 55.0],
                        [38.0, 56.0],
                        [37.0, 56.0],
                    ],
                ],
                [
                    [
                        [87, 85],
                        [87, 86],
                        [88, 85],
                    ],
                ],
            ]))
        polygons_array = MultiPolygon(geojson.MultiPolygon([
            [
                [
                    [37.0, 55.0],
                    [38.0, 55.0],
                    [38.0, 56.0],
                    [37.0, 56.0],
                    [37.0, 55.0],
                ],
            ],
            [
                [
                    [87, 85],
                    [87, 86],
                    [88, 85],
                    [87, 85],
                ],
            ],
        ]))
        tap.ok(polygons_array, 'Массив полигонов')

        serialized = polygons_array.pure_python()
        tap.eq(
            serialized,
            {
                "geometry": {
                    "coordinates": [
                        [
                            [
                                [37.0, 55.0],
                                [38.0, 55.0],
                                [38.0, 56.0],
                                [37.0, 56.0],
                                [37.0, 55.0],
                            ],
                        ],
                        [
                            [
                                [87, 85],
                                [87, 86],
                                [88, 85],
                                [87, 85],
                            ]
                        ]
                    ],
                    "type": "MultiPolygon"
                },
                "properties": {},
                "type": "Feature",
            },
            'Сереализация GeoJSON'
        )

        deserialized = MultiPolygon(serialized)
        tap.eq(polygons_array, deserialized, 'Десериализация из GeoJSON')
