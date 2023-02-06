# coding: utf-8
# pylint: disable=redefined-outer-name
from tempfile import TemporaryFile

import pytest
from cyson import Writer, OutputStream  # pylint: disable=no-name-in-module

from dmp_suite.geo_zone import CityGeoZone, create_city_detector_from_handbook


def make_city(id_, geometry):
    return {"areas": {"city": {"geometry": geometry}}, "id": id_, "tz": None}


def create_city_detector(records):
    with TemporaryFile() as handbook:
        writer = Writer(OutputStream.from_file(handbook), mode="list_fragment")

        writer.begin_stream()
        for record in records:
            writer.write(record)
        writer.end_stream()

        handbook.seek(0)
        return create_city_detector_from_handbook(CityGeoZone, handbook)


@pytest.fixture(scope="session")
def city_detector():
    return create_city_detector(
        [
            make_city("a", [[(3, 0), (3, 4), (7, 4), (7, 0)]]),
            make_city(
                "b",
                [
                    [(6, 0), (6, 4), (10, 4), (10, 0)],
                    [(7, 1), (7, 3), (9, 3), (9, 1)],  # A hole.
                ],
            ),
        ]
    )


@pytest.mark.parametrize(
    "given_lon, given_lat, expect_cities",
    [
        (1, 2, []),
        (5, 2, ["a"]),
        (6.5, 2, ["b", "a"]),
        (8, 2, []),
        (9.5, 2, ["b"]),
        (11, 2, []),
    ],
)
def test_city_detector(given_lon, given_lat, expect_cities, city_detector):
    assert city_detector.as_attr("id").get_all(given_lon, given_lat) == expect_cities
