# pylint: disable=redefined-outer-name
from operator import itemgetter
from hashlib import md5

import pytest

from qb2.api.v1 import resources as qr
from nile.api.v1 import Record

from dmp_suite.qb2 import extractors as dmp_qe
from dmp_suite.geo_zone import GeoareasHandbook, GeoareaGeoZone
from dmp_suite.tariffs import TariffsHandbook, TariffZoneData


def make_geoarea(name, id_, coordinates):
    return GeoareaGeoZone(
        Record(name=name, id=id_, geometry=dict(coordinates=coordinates), area=None)
    )


@pytest.fixture(scope="session")
def mock_geoareas_handbook():
    return qr.const(
        GeoareasHandbook(
            [
                make_geoarea("activation_a", "1", [[(0, 0), (0, 4), (4, 4), (4, 0)]]),
                make_geoarea("activation_b", "2", [[(3, 0), (3, 4), (7, 4), (7, 0)]]),
                make_geoarea(
                    "auxiliary_c",
                    "3",
                    [
                        [(6, 0), (6, 4), (10, 4), (10, 0)],
                        [(7, 1), (7, 3), (9, 3), (9, 1)],  # A hole.
                    ],
                ),
                make_geoarea("tariff_a", "4", [[(0, 0), (0, 1), (1, 1), (1, 0)]]),
                make_geoarea("tariff_b", "5", [[(6, 3), (6, 4), (7, 4), (7, 3)]]),
            ]
        )
    )


# fmt: off
@pytest.fixture(scope="session")
def mock_tariffs_handbook():
    return qr.const(
        TariffsHandbook(
            [
                Record(activation_zone="activation_a", home_zone="tariff_a", categories=[{"name": "x"}, {"name": "y"}]),
                Record(activation_zone="activation_b", home_zone="tariff_b", categories=[{"name": "z"}]),
                Record(activation_zone="activation_b", home_zone="nonexistent_d", categories=[{"name": "t"}]),
                Record(activation_zone="nonexistent_e", home_zone="tariff_b", categories=[{"name": "s"}]),
            ]
        )
    )


FACTS = [
    dict(lon=1, lat=2, geoareas=["activation_a"], tariff_zone="tariff_a",
         nearest_tariff_zone="tariff_a", activation_zone="activation_a", possible_tariffs={"x", "y"}),
    dict(lon=3.2, lat=2, geoareas=["activation_a", "activation_b"], tariff_zone="tariff_a",
         nearest_tariff_zone="tariff_a", activation_zone="activation_a", possible_tariffs={"x", "y"}),
    dict(lon=3.8, lat=2, geoareas=["activation_a", "activation_b"], tariff_zone="tariff_b",
         nearest_tariff_zone="tariff_b", activation_zone="activation_b", possible_tariffs={"z"}),
    dict(lon=5, lat=2, geoareas=["activation_b"], tariff_zone="tariff_b",
         nearest_tariff_zone="tariff_b", activation_zone="activation_b", possible_tariffs={"z"}),
    dict(lon=6.5, lat=2, geoareas=["activation_b", "auxiliary_c"], tariff_zone="tariff_b",
         nearest_tariff_zone="tariff_b", activation_zone="activation_b", possible_tariffs={"z"}),
    dict(lon=8, lat=2, geoareas=[], tariff_zone=None, nearest_tariff_zone="tariff_b"),
    dict(lon=9.5, lat=2, geoareas=["auxiliary_c"], tariff_zone=None, nearest_tariff_zone="tariff_b"),
    dict(lon=11, lat=2, geoareas=[], tariff_zone=None, nearest_tariff_zone="tariff_b"),
    dict(lon=1, lat=5, geoareas=[], tariff_zone=None, nearest_tariff_zone="tariff_a"),
    dict(lon=5, lat=5, geoareas=[], tariff_zone=None, nearest_tariff_zone="tariff_b"),
]
# fmt: on


def get_tariff_zone_data(fact):
    if fact["tariff_zone"] is None:
        return None
    return TariffZoneData(
        fact["activation_zone"], fact["tariff_zone"], fact["possible_tariffs"]
    )


@pytest.mark.parametrize(
    "given_lon, given_lat, expect_tariff_zone",
    map(itemgetter("lon", "lat", "tariff_zone"), FACTS),
)
def test_tariff_zone_from_coordinates(
    given_lon,
    given_lat,
    expect_tariff_zone,
    mock_geoareas_handbook,
    mock_tariffs_handbook,
):
    extractor = dmp_qe.tariff_zone_from_coordinates(
        "tariff_zone",
        "lon",
        "lat",
        geoareas_handbook=mock_geoareas_handbook,
        tariffs_handbook=mock_tariffs_handbook,
    )
    assert extractor(lon=given_lon, lat=given_lat) == expect_tariff_zone


@pytest.mark.parametrize(
    "given_lon, given_lat, expect_tariff_zone, strict_tariff_zone",
    map(itemgetter("lon", "lat", "nearest_tariff_zone", "tariff_zone"), FACTS),
)
def test_nearest_tariff_zone_from_coordinates(
    given_lon,
    given_lat,
    expect_tariff_zone,
    strict_tariff_zone,
    mock_geoareas_handbook,
    mock_tariffs_handbook,
):
    extractor = dmp_qe.nearest_tariff_zone_from_coordinates(
        "tariff_zone",
        "lon",
        "lat",
        geoareas_handbook=mock_geoareas_handbook,
        tariffs_handbook=mock_tariffs_handbook,
    )
    assert extractor(lon=given_lon, lat=given_lat) == dict(tariff_zone=expect_tariff_zone,
                                                           strict=strict_tariff_zone is not None)


@pytest.mark.parametrize(
    "given_lon, given_lat, expect_geoareas",
    map(itemgetter("lon", "lat", "geoareas"), FACTS),
)
def test_geoareas_from_coordinates(
    given_lon, given_lat, expect_geoareas, mock_geoareas_handbook
):
    extractor = dmp_qe.geoareas_from_coordinates(
        "geoareas", "lon", "lat", geoareas_handbook=mock_geoareas_handbook
    )
    assert sorted(extractor(lon=given_lon, lat=given_lat)) == sorted(expect_geoareas)


@pytest.mark.parametrize(
    "given_lon, given_lat, given_geoareas, expect_tariff_zone",
    map(itemgetter("lon", "lat", "geoareas", "tariff_zone"), FACTS),
)
def test_tariff_zone_from_geoareas(
    given_lon,
    given_lat,
    given_geoareas,
    expect_tariff_zone,
    mock_geoareas_handbook,
    mock_tariffs_handbook,
):
    extractor = dmp_qe.tariff_zone_from_geoareas(
        "tariff_zone",
        "lon",
        "lat",
        "geoareas",
        geoareas_handbook=mock_geoareas_handbook,
        tariffs_handbook=mock_tariffs_handbook,
    )
    assert (
        extractor(lon=given_lon, lat=given_lat, geoareas=given_geoareas)
        == expect_tariff_zone
    )


@pytest.mark.parametrize(
    "given_lon, given_lat, expect_tariff_zone_data",
    [(fact["lon"], fact["lat"], get_tariff_zone_data(fact)) for fact in FACTS],
)
def test_tariff_zone_data_from_coordinates(
    given_lon,
    given_lat,
    expect_tariff_zone_data,
    mock_geoareas_handbook,
    mock_tariffs_handbook,
):
    extractor = dmp_qe.tariff_zone_data_from_coordinates(
        "tariff_zone",
        "lon",
        "lat",
        geoareas_handbook=mock_geoareas_handbook,
        tariffs_handbook=mock_tariffs_handbook,
    )
    assert extractor(lon=given_lon, lat=given_lat) == expect_tariff_zone_data


@pytest.mark.parametrize(
    "given_driver_id, expect_driver_uuid",
    [
        ("abra_cadabra", "cadabra"),
        ("cadabra", None),
        ("", None),
        (None, None),
    ]
)
def test_driver_uuid_from_driver_id(given_driver_id, expect_driver_uuid):
    extractor = dmp_qe.driver_uuid_from_driver_id(
        "driver_uuid", "driver_id"
    )
    assert extractor(driver_id=given_driver_id) == expect_driver_uuid


@pytest.mark.parametrize(
    "given_fields, expect_surrogate_key",
    [
        pytest.param(
            {"id_a": "foo", "id_b": "bar"}, md5(b"foo.._..bar").hexdigest()
        ),
        pytest.param(
            {"id_a": "foo", "id_b": 42}, None, marks=pytest.mark.xfail(raises=TypeError)
        ),
        pytest.param(
            {"id_a": "foo", "id_b": None}, None, marks=pytest.mark.xfail(raises=TypeError)
        ),
    ]
)
def test_deprecated_surrogate_key(given_fields, expect_surrogate_key):
    extractor = dmp_qe.deprecated_surrogate_key(
        "id", "id_a", "id_b"
    )
    assert extractor(**given_fields) == expect_surrogate_key


# этот набор данных используется как для тестирования nile экстрактора так и для GP
data_for_check = [
    pytest.param(
        {
            "id1": "b542561e49414e51861bff9c38c2a4ed",
            "id2": "00845dcee53a4c9d92f84e40bb2e0c3a"
        },
        "0b8c0cd6-26fd-3eb4-a34e-8bb0da454e85"
    ),
    pytest.param(
        {
            "id1": "b542561e49414e51861bff9c38c2a4ed"*50,
            "id2": "00845dcee53a4c9d92f84e40bb2e0c3a"*50,
            "id4": "123",
        },
        "44fcd6a1-2efd-cfa8-520b-c0a394d0333c"
    ),
    pytest.param(
        {
            "id1": "",
            "id2": "00845dcee53a4c9d92f84e40bb2e0c3a",
            "id4": "",
        },
        "1f5646b2-5cf7-820f-95c8-5187231da0c7"
    ),
    pytest.param(
        {
            "id1": "",
            "id4": "",
        },
        "8b07a865-8261-8ed5-c7da-f2afee209c7a"
    ),
    pytest.param(
        {
            "id1": None,
            "id2": "00845dcee53a4c9d92f84e40bb2e0c3a"
        },
        "6ade9078-0e59-0555-a6b3-a94c48f673a7"
    ),
    pytest.param(
        {
            "id1": None,
            "id2": None
        },
        None
    ),
    pytest.param(
        {
            "id1": "1",
            "id2": 1,
        },
        '08de562f-6650-3510-c831-a767babab341'
    ),
    pytest.param(
        {
            "id1": None,
            "id2": 1,
        },
        "a3afd0b3-d24f-2e8b-d2c7-8000f30d259b"
    ),
]

@pytest.mark.parametrize(
    "given_fields, expected_surrogate_key",
    data_for_check
)
def test_hnhm_surrogate_key(given_fields, expected_surrogate_key):
    extractor = dmp_qe.hnhm_surrogate_key(
        'sk', *given_fields.keys()
    )
    if isinstance(expected_surrogate_key, Exception):
        with pytest.raises(expected_surrogate_key):
            extractor(**given_fields)
    else:
        assert extractor(**given_fields) == expected_surrogate_key
