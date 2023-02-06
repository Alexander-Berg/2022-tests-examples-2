import re

import pytest

from sandbox.projects.release_machine.components.configs import all as all_cfg
from sandbox.projects.release_machine.components.configs import Responsible, Abc
from sandbox.projects.release_machine.components.config_core import responsibility


ACCEPTABLE_CUBE_NAME_PATTERN = re.compile("[_a-z][a-z0-9_]+")


@pytest.mark.parametrize(
    "cfg",
    [all_cfg.get_config(component_name) for component_name in all_cfg.get_all_ci_names()],
)
class TestRmOverCiConfigs:

    def test__abc_service_present(self, cfg):

        cls_name = cfg.__class__.__name__

        assert isinstance(cfg.responsible, Responsible), (
            f"{cls_name}.responsible: wrong type (expected Responsible, got {type(cfg.responsible)})"
        )
        assert cfg.responsible.abc is not None, (
            f"{cls_name}.responsible: abc missing"
        )
        assert isinstance(cfg.responsible.abc, Abc), (
            f"{cls_name}.responsible.abc: wrong type (expected Abc, got {type(cfg.responsible.abc)})"
        )

    def test__ci_block(self, cfg):

        for attr_name in ("a_yaml_dir", "secret", "sb_owner_group"):
            assert getattr(cfg.ci_cfg, attr_name), f"Missing {cfg.__class__.__name__}.CI.{attr_name}"

    def test__jg_cube_names_snake_case(self, cfg):

        if not cfg.uses_newstyle_jg:  # old-style ci configs - skipping
            return

        for action_name, action_data in cfg.jg.all_actions.items():

            for cube in action_data.graph.all_cubes_iter:

                assert isinstance(cube.name, str)
                assert len(cube.name) <= 100, f"Cube {cube.name} name is too big. Names need to be smaller than 100 symbols. (RMDEV-3263)"
                assert ACCEPTABLE_CUBE_NAME_PATTERN.fullmatch(cube.name), (
                    "{}.{}: '{}' - should use snake_case for cube names".format(
                        cfg.name,
                        action_name,
                        cube.name,
                    )
                )

    def test__ci__config_edit_approvals(self, cfg):

        assert isinstance(cfg.ci_cfg.config_edit_approvals, list)

        errors = []

        for index, approver in enumerate(cfg.ci_cfg.config_edit_approvals):

            if not isinstance(approver, responsibility.ABCSelection):
                errors.append("[{}] {} ({})".format(index, approver, type(approver)))

        error_str = "\n- ".join(errors)

        assert not errors, (
            f"{cfg.name}.ci_cfg.config_edit_approvals wrong types found (expected responsibility.ABCSelection: \n"
            f"- {error_str}\n"
        )
