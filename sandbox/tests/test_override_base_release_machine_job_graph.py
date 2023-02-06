from sandbox.projects.release_machine.components.config_core.bases.ci import ReferenceCIConfig
from sandbox.projects.release_machine.components.config_core.jg import base as jg_base
from sandbox.projects.release_machine.components.config_core.jg import flow as jg_flow
from sandbox.projects.release_machine.components.config_core.jg import cube as jg_cube
from sandbox.projects.release_machine.components.config_core.jg.cube.lib import build as build_cubes
from sandbox.projects.release_machine.components.config_core.jg.cube.lib import release as release_cubes


class MainTestCfg(ReferenceCIConfig):
    name = "test_component"
    responsible = "robot-srch-releaser"

    class CI(ReferenceCIConfig.CI):
        secret = "abcdefghij"
        sb_owner_group = "XXXXXX"
        a_yaml_dir = "whatever/suits/the/test/needs"

    class JG(jg_base.BaseReleaseMachineJobGraph):

        @jg_flow.release_flow()
        def release(self):
            graph = super(self.__class__, self).release(self)

            build = build_cubes.YaMake2(
                targets="/path/to/my/target",
                artifacts="/path/to/my/target=my_target",
                resource_types="MY_RESOURCE",
                name="build",
                needs=[
                    graph.get("new_tag"),
                ],
            )

            release = release_cubes.ReleaseRmComponent2(
                component_name=self.component_name,
                where_to_release="stable",
                input=jg_cube.CubeInput(
                    component_resources={
                        "my_resource": build.output.resources["MY_RESOURCE"].first(),
                    },
                ),
            )

            graph.add(build)
            graph.add(release)

            return graph


def test__override_base_release_machine_job_graph_class():
    assert hasattr(jg_base.BaseReleaseMachineJobGraph, "flow_funcs")
    assert "release" in jg_base.BaseReleaseMachineJobGraph.flow_funcs


def test__override_base_release_machine_job_graph_subclass():
    assert hasattr(MainTestCfg.JG, "flow_funcs")
    assert "release" in MainTestCfg.JG.flow_funcs


def test__override_base_release_machine_job_graph():

    cfg = MainTestCfg()

    assert hasattr(cfg, "jg")
    assert isinstance(cfg.jg, jg_base.JGCfg)
    assert len(cfg.jg.non_release_actions) == 0
    assert len(cfg.jg.release_actions) == 1
    assert "release_test_component" in cfg.jg.release_actions

    release_flow = cfg.jg.release_actions["release_test_component"]

    assert not release_flow.action_parameters.auto
    assert release_flow.action_parameters.triggers is None

    assert release_flow.action_parameters.branches is not None
    assert release_flow.action_parameters.branches.pattern == cfg.svn_cfg.arc_branch_path("${version}")
    assert release_flow.action_parameters.branches.auto_create is True
    assert not release_flow.action_parameters.branches.forbid_trunk_releases

    branches_dict = release_flow.action_parameters.branches.to_dict()

    assert "pattern" in branches_dict
    assert "auto-create" in branches_dict
    assert "forbid-trunk-releases" in branches_dict

    all_cube_names = {c.name for c in release_flow.graph.all_cubes_iter}

    assert all_cube_names == {
        "release__test_component__stable", "build", "new_tag", "create_changelog",
        "create_startrek_ticket", "link_feature_tickets", "format_changelog", "post_changelog_to_startrek",
        "main_graph_entry",
    }
