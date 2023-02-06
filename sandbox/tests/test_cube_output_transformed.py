import pytest

from sandbox.projects.release_machine.components.config_core.jg.cube import base as cube_base


def get_test_cube(name):
    return cube_base.Cube(name=name, task="test/jg/cube/cube_output_transformed/{}".format(name))


@pytest.fixture(scope="module")
def cube_1():
    return get_test_cube("cube_1")


@pytest.fixture(scope="module")
def cube_2():
    return get_test_cube("cube_2")


@pytest.fixture(scope="module")
def cube_3():
    return get_test_cube("cube_3")


def test__incorrect_transform_function(cube_1, cube_2, cube_3):
    with pytest.raises(TypeError):
        cube_base.CubeOutputTransformed(
            [cube_1.output.f1, cube_2.output.f2, cube_3.output.f3],
            int,
        )


def test__correct_declaration(cube_1, cube_2, cube_3):

    cot = cube_base.CubeOutputTransformed(
        [cube_1.output.f1, cube_2.output.f2, cube_3.output.f3],
        lambda l: ",".join(l),
    )

    expected_value = "${tasks.cube_1.f1},${tasks.cube_2.f2},${tasks.cube_3.f3}"

    assert cube_base.CubeInput.format_input_dict_item_value(cot) == expected_value
