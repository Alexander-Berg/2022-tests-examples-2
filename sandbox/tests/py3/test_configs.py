import pytest

from sandbox.projects.release_machine.components.configs import all as all_cfg
from sandbox.projects.release_machine.components.configs import Responsible

from sandbox.projects.release_machine.core import const as rm_const


@pytest.fixture(scope="function", params=all_cfg.get_all_names())
def component_name(request):
    return request.param


def test_config_general_attributes(component_name):

    try:

        c_cfg = all_cfg.get_config(component_name)

        assert isinstance(c_cfg.name, str)
        assert isinstance(c_cfg.display_name, str)
        assert isinstance(c_cfg.responsible, (str, Responsible))

    except (NameError, AttributeError, SyntaxError):
        assert False


def test_no_new_rmte_components_should_appear(component_name):
    """Fail if new RM over TE component appears"""

    c_cfg = all_cfg.get_config(component_name)

    assert c_cfg.release_cycle_type == rm_const.ReleaseCycleType.CI or c_cfg.name in rm_const.KNOWN_RMTE_COMPONENTS, (
        "Please, do NOT create new RM over TE components. "
        "RM over CI is the only supported component type at the moment. "
        "See https://wiki.yandex-team.ru/releasemachine/rm-over-ci/"
    )


def test_module_loading():

    loading_errors = None

    try:
        all_cfg.scan_all_modules_and_raise_on_errors()
    except all_cfg.ReleaseMachineConfigModuleLoaderError as rmcmle:
        loading_errors = f"{rmcmle}"

    assert not loading_errors, "RM config loading error: {}".format(loading_errors)
