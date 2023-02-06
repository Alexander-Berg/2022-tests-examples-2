from sandbox.projects.release_machine.components.config_core.jg.graph import base as graph_base
from sandbox.projects.release_machine.components.config_core.jg.cube import base as cube_base


def test__graph_initialization():

    c0 = cube_base.Cube(
        task="projects/release_machine/create_arc_tag",
    )

    c1 = cube_base.Cube(
        task="projects/release_machine/get_or_create_st_ticket",
        needs=[c0],
    )

    c2 = cube_base.Cube(
        task="projects/release_machine/link_feature_tickets_from_changelog",
        input=cube_base.CubeInput(
            ticket_key=c1.output.st_ticket.key,
        ),
    )

    c3 = cube_base.Cube(
        task="projects/release_machine/post_startrek_comment",
        input=cube_base.CubeInput(
            issue_key=c1.output.st_ticket.key,
        ),
    )

    g = graph_base.Graph([c0, c1, c2, c3])

    assert c0 in g
    assert c1 in g
    assert c2 in g
    assert c3 in g


def test__graph_add():
    c0 = cube_base.Cube(
        task="projects/release_machine/create_arc_tag",
    )

    g = graph_base.Graph([c0])

    c1 = cube_base.Cube(
        task="projects/release_machine/get_or_create_st_ticket",
        needs=[c0],
    )

    g.add(c1)

    assert c0 in g
    assert c1 in g


def test__graph_get():
    c0 = cube_base.Cube(
        name="c0",
        task="projects/release_machine/create_arc_tag",
    )

    g = graph_base.Graph([c0])

    c1 = cube_base.Cube(
        name="c1",
        task="projects/release_machine/get_or_create_st_ticket",
        needs=[c0],
    )

    g.add(c1)

    assert c0 is g.get("c0")
    assert c1 is g.get("c1")


def test__graph_populate_with_requirements():
    c0 = cube_base.Cube(
        name="c0",
        task="projects/release_machine/create_arc_tag",
    )

    c1 = cube_base.Cube(
        name="c1",
        task="projects/release_machine/get_or_create_st_ticket",
        needs=[c0],
    )

    c2 = cube_base.Cube(
        task="projects/release_machine/link_feature_tickets_from_changelog",
        input=cube_base.CubeInput(
            ticket_key=c1.output.st_ticket.key,
        ),
    )

    g = graph_base.Graph([c2])

    assert c2 in g
    assert c1 not in g
    assert c0 not in g

    g.populate_with_requirements()

    assert c0 in g
    assert c1 in g
