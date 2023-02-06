from sandbox.projects.release_machine.components.config_core import jg
from sandbox.projects.release_machine.components.config_core.jg.graph import base as graph_base
from sandbox.projects.release_machine.components.config_core.jg.cube import base as cube_base


class RootCfgMock(object):

    name = "test_component"

    class SvnCfg(object):
        start_version = 0

    def __init__(self):
        self.svn_cfg = self.SvnCfg()


class MainTestJGCfg(jg.JGCfg):

    def _get_build(self, new_tag_cube=None):
        return cube_base.Cube(
            name="build",
            task="common/arcadia/ya_make",
            input=cube_base.CubeInput(
                targets="release_machine/iceflame/bin/iceflame",
            ),
            needs=[new_tag_cube] if new_tag_cube else None,
        )

    def _base_release_flow(self):

        new_tag = cube_base.Cube(
            task="projects/release_machine/create_arc_tag",
        )

        create_st_ticket = cube_base.Cube(
            task="projects/release_machine/get_or_create_st_ticket",
            needs=[new_tag],
        )

        link_tickets = cube_base.Cube(
            task="projects/release_machine/link_feature_tickets_from_changelog",
            input=cube_base.CubeInput(
                ticket_key=create_st_ticket.output.st_ticket.key,
            ),
        )

        post_comment = cube_base.Cube(
            task="projects/release_machine/post_startrek_comment",
            input=cube_base.CubeInput(
                issue_key=create_st_ticket.output.st_ticket.key,
            ),
        )

        build = self._get_build(new_tag)

        return graph_base.Graph(
            [
                new_tag,
                create_st_ticket,
                link_tickets,
                post_comment,
                build,
            ]
        )

    def _get_release_cube(self, where, build_cube):
        return cube_base.Cube(
            name="release_{}".format(where),
            task="RELEASE_RM_COMPONENT_2",
            input=cube_base.CubeInput(
                where_to_release=where,
                component_resources={
                    "release_item_name": build_cube.output.resources["?type == ''MY_SHINY_BUILD''"][0].id,
                },
            ),
        )

    @jg.register_flow(
        kind="release",
        branches=jg.ActionBranches(pattern="releases/test_jg/${version}", auto_create=True),
    )  # this is not the best approach, it's used here only for test purpose
    def stable_release_flow(self):

        graph = self._base_release_flow()

        release = self._get_release_cube("stable", graph.get("build"))

        graph.add(release)

        return graph

    @jg.register_flow(kind="action", auto=True, triggers=[jg.ActionTrigger("commit")])
    def testing_release_flow(self):

        build = self._get_build()
        release = self._get_release_cube("testing", build)

        return graph_base.Graph([build, release])


def test__jg_cfg_class():
    assert hasattr(MainTestJGCfg, "flow_funcs")
    assert "stable_release_flow" in MainTestJGCfg.flow_funcs
    assert "testing_release_flow" in MainTestJGCfg.flow_funcs


def test__jg_cfg_instance():

    jg_cfg = MainTestJGCfg(root_cfg=RootCfgMock())

    assert jg_cfg.release_actions
    assert len(jg_cfg.release_actions) == 1

    assert jg_cfg.non_release_actions
    assert len(jg_cfg.non_release_actions) == 1

    # todo

    assert "stable_release_flow" in jg_cfg.release_actions
    g = jg_cfg.release_actions["stable_release_flow"].graph
    assert g.get("release_{}".format("stable"))

    assert "testing_release_flow" in jg_cfg.non_release_actions
    g = jg_cfg.non_release_actions["testing_release_flow"].graph
    assert g.get("release_{}".format("testing"))
