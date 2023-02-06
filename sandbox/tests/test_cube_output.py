import pytest

from sandbox.projects.release_machine.components.config_core.jg.cube import base as cube_base
from sandbox.projects.release_machine.components.config_core.jg.lib import call_chain


@pytest.fixture(scope="session")
def rrc_cube():
    return cube_base.Cube(task="RELEASE_RM_COMPONENT_2")


def test__output_type(rrc_cube):
    assert isinstance(rrc_cube.output, cube_base.CubeOutput)


def test__output_getattr_type(rrc_cube):

    assert isinstance(rrc_cube.output.something, cube_base.CubeOutput)
    assert isinstance(rrc_cube.output.something.more.complex, cube_base.CubeOutput)


def test__output_getitem_type(rrc_cube):

    assert isinstance(rrc_cube.output.something[0], cube_base.CubeOutput)
    assert isinstance(rrc_cube.output.resources["SOMETHING"], cube_base.CubeOutput)
    assert isinstance(rrc_cube.output.resources["SOMETHING"][0].id, cube_base.CubeOutput)


def test__output__call_chain__complex(rrc_cube):

    output = rrc_cube.output.resources["?type == 'MY_SHINY_BUILD'"][0].id

    assert output.call_chain, "Output call chain unexpectedly None"
    assert isinstance(output.call_chain, call_chain.CallChainMem)
    assert output.call_chain.call_chain, "Output call chain unexpectedly empty"
    assert output.call_chain.jmespath == "resources | [?type == 'MY_SHINY_BUILD'] | [0].id"


def test__output__call_chain__resource_hack(rrc_cube):

    o1 = rrc_cube.output.resources["?type == 'MY_SHINY_BUILD'"][0].id
    o2 = rrc_cube.output.resources["MY_SHINY_BUILD"][0].id

    assert o1.call_chain.jmespath == o2.call_chain.jmespath
