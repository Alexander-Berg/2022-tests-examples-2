import pytest

from sandbox.projects.release_machine.components.config_core.jg.cube import base as cube_base
from sandbox.projects.release_machine.components.config_core.jg.cube.lib import metrics
from sandbox.projects.release_machine.components.config_core.jg.cube.lib import yappy


@pytest.fixture
def component_name():
    return "test_component"


@pytest.fixture
def search_subtype():
    return "test"


@pytest.fixture
def scraper_over_yt_pool():
    return "whatever"


def test__by_generate_beta_cube(component_name, search_subtype, scraper_over_yt_pool):

    gyb = yappy.GenerateYappyBeta(component_name=component_name, beta_conf_type=search_subtype)

    lm = metrics.LaunchMetrics.by_generate_beta_cube(
        gyb,
        input=cube_base.CubeInput(scraper_over_yt_pool=scraper_over_yt_pool),
    )

    assert isinstance(lm, metrics.LaunchMetrics)
    assert lm.component_name == component_name
    assert lm.input.get("search_subtype") == search_subtype
    assert lm.input.get("scraper_over_yt_pool") == scraper_over_yt_pool


def test__by_generate_beta_cube__type_error():

    with pytest.raises(TypeError):
        metrics.LaunchMetrics.by_generate_beta_cube(None)

    with pytest.raises(TypeError):
        metrics.LaunchMetrics.by_generate_beta_cube(cube_base.Cube("something", task="projects/somewhere"))
