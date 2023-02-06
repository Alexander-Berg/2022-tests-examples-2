import pytest

from ctaxi_pyml import example as pybind_objects
from taxi_pyml.example import objects as py_objects


@pytest.fixture
def simple_data():
    return {
        'point': [33, 55],
        'optional_point': [34, 56],
        'point_vector': [[35, 57], [36, 58]],
    }


@pytest.fixture
def object_data():
    return {'point': {'lon': 33, 'lat': 55}}


def test_geopoint_deserizelization_py(simple_data):
    obj = py_objects.GeoPointExample.deserialize(simple_data)
    assert obj.point[0] == 33
    assert obj.optional_point[0] == 34
    assert obj.point_vector[0][0] == 35


def test_geopoint_deserizelization_pybind(simple_data):
    obj = pybind_objects.GeoPointExample.deserialize(simple_data)
    assert obj.point.lon == 33
    assert obj.optional_point.lon == 34
    assert obj.point_vector[0].lon == 35


@pytest.mark.parametrize(
    'definitions_mod',
    [
        pytest.param(pybind_objects, id='pybind'),
        pytest.param(py_objects, id='py'),
    ],
)
def test_geopoint_serizelization(definitions_mod, simple_data):
    obj = definitions_mod.GeoPointExample.deserialize(simple_data)
    assert obj.serialize() == simple_data


def test_parse_serialize_as_object_py(object_data):
    obj = py_objects.GeoPointAsObjExample.deserialize(object_data)
    assert obj.serialize() == object_data


def test_parse_serialize_as_object_pybind(object_data):
    obj = pybind_objects.GeoPointAsObjExample.deserialize(object_data)
    # This happens because of awkward geo point binding implementation
    assert obj.serialize() != object_data
    assert obj.serialize() == {'point': [33, 55]}
