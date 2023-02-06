import pytest

from sandbox.projects.release_machine.components.config_core.bases.ci import ReferenceCIConfig
from sandbox.projects.release_machine.components.config_core.jg import base as jg_base


class MainTestCfg(ReferenceCIConfig):
    name = "test_component"
    responsible = "robot-srch-releaser"

    class CI(ReferenceCIConfig.CI):
        secret = "abcdefghij"
        sb_owner_group = "XXXXXX"
        a_yaml_dir = "whatever/suits/the/test/needs"

    class JG(jg_base.BaseReleaseMachineJobGraph):
        pass


@pytest.fixture(scope="session")
def main_cfg():
    return MainTestCfg()


def test__base_release_machine_job_graph_class():
    assert hasattr(jg_base.BaseReleaseMachineJobGraph, "flow_funcs")
    assert "release" in jg_base.BaseReleaseMachineJobGraph.flow_funcs


def test__base_release_machine_job_graph_subclass():
    assert hasattr(MainTestCfg.JG, "flow_funcs")
    assert "release" in MainTestCfg.JG.flow_funcs


def test__base_release_machine_job_graph(main_cfg):

    assert hasattr(main_cfg, "jg")
    assert isinstance(main_cfg.jg, jg_base.JGCfg)
    assert len(main_cfg.jg.non_release_actions) == 0
    assert len(main_cfg.jg.release_actions) == 1
    assert "release_test_component" in main_cfg.jg.release_actions

    release_flow = main_cfg.jg.release_actions["release_test_component"]

    assert not release_flow.action_parameters.auto
    assert release_flow.action_parameters.triggers is None

    assert release_flow.action_parameters.branches is not None
    assert release_flow.action_parameters.branches.pattern == main_cfg.svn_cfg.arc_branch_path("${version}")
    assert release_flow.action_parameters.branches.auto_create is True
    assert not release_flow.action_parameters.branches.forbid_trunk_releases

    branches_dict = release_flow.action_parameters.branches.to_dict()

    assert "pattern" in branches_dict
    assert "auto-create" in branches_dict
    assert "forbid-trunk-releases" in branches_dict

    all_cube_names = {c.name for c in release_flow.graph.all_cubes_iter}

    assert all_cube_names == {
        "new_tag", "create_changelog", "create_startrek_ticket", "link_feature_tickets",
        "format_changelog", "post_changelog_to_startrek", "main_graph_entry",
    }


@pytest.mark.parametrize(
    "tested_cube_name, expected_cube_name_list",
    [
        ("main_graph_entry", ["new_tag"]),
        ("create_changelog", ["main_graph_entry"]),
        ("create_startrek_ticket", ["main_graph_entry"]),
        ("format_changelog", ["create_changelog"]),
        ("post_changelog_to_startrek", ["format_changelog"]),
        ("link_feature_tickets", ["create_startrek_ticket", "create_changelog"]),
    ]
)
def test__base_release_machine_job_graph__cube_requirements(tested_cube_name, expected_cube_name_list, main_cfg):

    assert main_cfg.notify_cfg.use_startrek, "Test misconfiguration: the test config has use_startrek set to False, " \
                                             "which makes test__base_release_machine_job_graph__cube_requirements " \
                                             "not applicable"

    tested_cube = main_cfg.jg.release_actions["release_test_component"].graph.get(tested_cube_name)
    req_fail = "'{}' cube missing '{{}}' in requirements".format(tested_cube_name)

    for expected_cube_name in expected_cube_name_list:
        expected_cube = main_cfg.jg.release_actions["release_test_component"].graph.get(expected_cube_name)

        assert expected_cube in tested_cube.requirements, req_fail.format(expected_cube_name)
