import pytest

from sandbox.projects.release_machine.components.config_core.jg.cube import base
from sandbox.projects.release_machine.components.config_core.jg.cube import exceptions
from sandbox.projects.release_machine.core import const as rm_const


def test__cube_requirements():

    a = base.Cube(name="a", task="YA_MAKE_2")
    b = base.Cube(
        name="b",
        task="YA_MAKE_2",
        input=base.CubeInput(
            input_field=a.output.output_field,
        ),
    )

    assert a in b.requirements

    c = base.Cube(
        name="c",
        task="YA_MAKE_2",
        input=base.CubeInput(
            f1=a.output.f.some.value,
            f2=b.output.f.another.value,
        ),
    )

    assert a in c.requirements and b in c.requirements


def test__cube_to_dict():

    a = base.Cube(name="a", task="YA_MAKE_2")
    b = base.Cube(
        name="b",
        task="YA_MAKE_2",
        input=base.CubeInput(
            input_field=a.output.output_field,
        ),
        manual=False,
    )

    c = base.Cube(
        name="c",
        task="YA_MAKE_2",
        input=base.CubeInput(
            f1=a.output.f.some.value,
            f2=b.output.f.another.value,
        ),
        manual=True,
    )

    b_dict = b.to_dict()["b"]
    c_dict = c.to_dict()["c"]

    for test_dict in [b_dict, c_dict]:

        assert "title" in test_dict
        assert "task" in test_dict
        assert "needs" in test_dict
        assert "input" in test_dict

    assert isinstance(b_dict["needs"], list)
    assert a.name in b_dict["needs"]

    assert isinstance(c_dict["needs"], list)
    assert a.name in c_dict["needs"]
    assert b.name in c_dict["needs"]

    assert "manual" in c_dict
    assert bool(c_dict["manual"])
    assert bool(c.manual)

    assert "manual" not in b_dict
    assert not bool(b.manual)


def test__cube_cannot_exist_without_a_task():

    with pytest.raises(exceptions.CubeInitializationError):
        base.Cube()


def test__cube_set_name__construct__good():

    c = base.Cube(task="YA_MAKE_2")

    c.set_name({"a", "b"})

    assert c.name == "default_ya_make_2"


def test__cube_set_name__construct_with_index__good():

    c = base.Cube(task="YA_MAKE_2")

    c.set_name({"default_ya_make_2", "default_ya_make_2_1"})

    assert c.name == "default_ya_make_2_2"


def test__cube_set_name__predefined__good():

    c = base.Cube(name="something", task="YA_MAKE_2")

    c.set_name({"a", "b"})

    assert c.name == "something"


def test__cube_set_name__predefined__bad():

    c = base.Cube(name="something", task="YA_MAKE_2")

    with pytest.raises(exceptions.CubeNamingError):
        c.set_name({"a", "b", "something"})


def test__cube_set_task__sandbox_task__good():

    for item in rm_const.TASK_CI_REG_LOCATIONS:
        c = base.Cube(task=item)
        assert c.task_path == rm_const.TASK_CI_REG_LOCATIONS[item]


def test__cube_set_task__sandbox_task__bad():

    with pytest.raises(exceptions.CubeInitializationError):
        base.Cube(task="UNKNOWN_UNEXPECTED_TASK")


def test__cube_set_task__ci_registry_path__good():
    path = "common/arcadia/ya_make"
    c = base.Cube(task=path)
    assert c.task_path == path


def test__cube_complex_dependencies():

    c1 = base.Cube(task="common/arcadia/task_1")
    c2 = base.Cube(task="common/arcadia/task_2")
    c3 = base.Cube(task="common/arcadia/task_3")
    c4 = base.Cube(task="common/arcadia/task_4")
    c5 = base.Cube(task="common/arcadia/task_5")

    c_main = base.Cube(
        task="common/arcadia/task_2",
        input=base.CubeInput(
            inline_field=c1.output.some_field,
            dict_field={
                "some_simple_key": "some_simple_value",
                "some_key": c2.output.resources["SOME_RESOURCE"][0].id,
                "some_other_key": c5.output.resources["SOME_RESOURCE"].first(),
            },
            list_field=[
                c3.output.l1,
                c4.output.l2,
            ],
        ),
    )

    assert c_main.requirements, "Input requirements are not managed properly"

    assert c1 in c_main.requirements, "Inline input requirement failure"
    assert c2 in c_main.requirements, "Dict input requirement failure"
    assert c3 in c_main.requirements, "List input requirement failure (value #0)"
    assert c4 in c_main.requirements, "List input requirement failure (value #1)"
    assert c5 in c_main.requirements, "Dict input requirement failure (resource selector with .first())"


def test__cube_clone():

    c0 = base.Cube(task="base/task", name="c0")
    c1 = base.Cube(task="my/task", name="c1", needs=[c0])
    c2 = c1.clone()

    c2.set_name(all_names={c1.name, c0.name})

    assert c2 is not c1
    assert c2.name != c1.name
    assert c2.task_name == c1.task_name
    assert c2.task_path == c1.task_path
    assert c2.requirements == c1.requirements


def test__cube_circular_dependencies__input():

    c1 = base.Cube(name="c1", task="some/task/t1")
    c2 = base.Cube(name="c2", task="some/task/t2")

    c1.input.update(field_2=c2.output.field_2)
    c2.input.update(field_1=c1.output.field_1)

    with pytest.raises(exceptions.CubeCircularDependencyError):
        c1.requirements

    with pytest.raises(exceptions.CubeCircularDependencyError):
        c2.requirements


def test__cube_circular_dependencies__custom_requirements():

    c1 = base.Cube(name="c1", task="some/task/t1")
    c2 = base.Cube(name="c2", task="some/task/t2")

    c1.add_requirement(c2)

    with pytest.raises(exceptions.CubeCircularDependencyError):
        c2.add_requirement(c1)


def test__cube_circular_dependencies__mixed():

    c1 = base.Cube(name="c1", task="some/task/t1")
    c2 = base.Cube(name="c2", task="some/task/t2")

    c1.add_requirement(c2)
    c2.input.update(field=c1.output.field)

    with pytest.raises(exceptions.CubeCircularDependencyError):
        c1.requirements

    with pytest.raises(exceptions.CubeCircularDependencyError):
        c2.requirements


def test__cube_circular_dependencies__chain():
    c1 = base.Cube(name="c1", task="some/task/t1")
    c2 = base.Cube(name="c2", task="some/task/t2")
    c3 = base.Cube(name="c3", task="some/task/t3")
    c4 = base.Cube(name="c4", task="some/task/t4")

    c2.add_requirement(c1)
    c3.add_requirement(c2)
    c4.add_requirement(c3)

    with pytest.raises(exceptions.CubeCircularDependencyError):
        c1.add_requirement(c4)


def test__cube_input__recursive_update():

    c = base.Cube(
        name="c",
        task="some/task",
        input=base.CubeInput(
            field_1={
                "field_1_1": 11,
                "field_1_2": 12,
            },
            field_2={
                "field_2_1": 21,
            },
            field_3=3,
        ),
    )

    c.input.update(field_1={"field_1_2": False}, field_3=333)

    assert "field_1_1" in c.input.input_dict["field_1"]
    assert c.input.input_dict["field_1"]["field_1_1"] == 11

    assert "field_1_2" in c.input.input_dict["field_1"]
    assert c.input.input_dict["field_1"]["field_1_2"] is False

    assert c.input.input_dict["field_3"] == 333


@pytest.mark.parametrize(
    ["orig", "upd", "expected"],
    [
        (
            {"a": 1},
            {"b": 2},
            {"a": 1, "b": 2},
        ),
        (
            {"a": 1},
            {"a": 2},
            {"a": 2},
        ),
        (
            {"a": {"b": 1}},
            {"a": {"c": 2}},
            {"a": {"b": 1, "c": 2}},
        ),
        (
            {"a": {"b": {"c": {"d": 1}}}},
            {"a": {"b": {"c2": {"d2": 2}}}},
            {"a": {"b": {"c": {"d": 1}, "c2": {"d2": 2}}}},
        ),
    ],
)
def test__cube_input__update_recursive__classmethod(orig, upd, expected):
    assert base.CubeInput.update_recursive(orig, upd) == expected
