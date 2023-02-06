import pytest

from core.transformation import TransformationsRegister, TransformRule, identity


@pytest.fixture
def transformation_register():
    return TransformationsRegister([
        TransformRule('string', ['varchar'], identity),
        TransformRule('uint16', ['int', 'int4'], identity),
    ])


def test_yt_types(transformation_register):
    assert transformation_register.yt_types == {'string', 'uint16'}


def test_gp_types(transformation_register):
    assert transformation_register.gp_types == {'varchar', 'int', 'int4'}


def test_get_transformations(transformation_register):
    assert identity == transformation_register.get_transformation('string')
