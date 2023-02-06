from __future__ import absolute_import

import pytest

from sandbox import sdk2
from sandbox.sdk2 import legacy


class TestParameterCasting(object):
    def test__arcadia_url(self):
        """ test casting of sandbox.sdk2.legacy.SandboxArcadiaUrlParameter """

        cast = legacy.SandboxArcadiaUrlParameter.cast

        arc_url = "arcadia-arc:/#trunk"
        assert cast(arc_url) == arc_url

        with pytest.raises(ValueError):
            cast("arcadia-arcas:/#trunk")

        with pytest.raises(ValueError):
            cast("arcadia-hgcas:/#trunk")

    def test__yav_secret_parameter(self):
        sec = "sec-123qwe"
        ver = "ver-asd456"
        key = "my_weired_key:;!@#$%^&*()"

        value = sdk2.parameters.YavSecret.cast("{}@{}#{}".format(sec, ver, key))
        assert value.secret.secret_uuid == sec
        assert value.secret.version_uuid == ver
        assert value.secret.default_key == value.default_key == key

        value = sdk2.parameters.YavSecret.cast("{}@{}".format(sec, ver))
        assert value.secret.secret_uuid == sec
        assert value.secret.version_uuid == ver
        assert value.default_key is None

        value = sdk2.parameters.YavSecret.cast(sec)
        assert value.secret.secret_uuid == sec
        assert value.secret.version_uuid is None
        assert value.default_key is None

        value = sdk2.parameters.YavSecret.cast("{}#{}".format(sec, key))
        assert value.secret.secret_uuid == sec
        assert value.secret.version_uuid is None
        assert value.default_key == key

    @pytest.mark.parametrize(
        "value",
        (
            "sec123eqw@ver53453",
            "SEC-123eqw",
            "sec-123eqw@ver-53453@ver-543",
        )
    )
    def test__yav_secret_erroneous_value(self, value):
        with pytest.raises(ValueError):
            sdk2.parameters.YavSecret.cast(value)

    def test__yav_secret_with_key_parameter(self):
        sec = "sec-123qwe"
        ver = "ver-asd456"
        key = "my_weired_key:;!@#$%^&*()"

        value = sdk2.parameters.YavSecretWithKey.cast("{}@{}#{}".format(sec, ver, key))
        assert value.secret.secret_uuid == sec
        assert value.secret.version_uuid == ver
        assert value.secret.default_key == value.default_key == key

        with pytest.raises(ValueError):
            sdk2.parameters.YavSecretWithKey.cast("{}@{}".format(sec, ver))

        with pytest.raises(ValueError):
            sdk2.parameters.YavSecretWithKey.cast(sec)

        value = sdk2.parameters.YavSecretWithKey.cast("{}#{}".format(sec, key))
        assert value.secret.secret_uuid == sec
        assert value.secret.version_uuid is None
        assert value.default_key == key


class TestParametersDefinition(object):
    def test__external_parameters(self):
        class CommonParams(sdk2.Parameters):
            a = sdk2.parameters.String("A")
            b = sdk2.parameters.String("B")

        class TestTaskWithExternalParams(sdk2.Task):
            class Parameters(sdk2.Task.Parameters):
                f = sdk2.parameters.Bool("F")
                with f.value[True]:
                    c = sdk2.parameters.String("C")
                    e = CommonParams()

        # noinspection PyTypeChecker
        common_names = {p.name for p in CommonParams}
        assert common_names == {"a", "b"}
        # noinspection PyTypeChecker
        assert {p.name for p in TestTaskWithExternalParams.Parameters} == common_names | {"f", "c"}
        assert set(TestTaskWithExternalParams.Parameters.f.sub_fields["true"]) == common_names | {"c", "e"}

    # noinspection PyUnusedLocal
    def test__noninstantiated_parameters(self):
        with pytest.raises(AssertionError):
            class Parameters1(sdk2.Parameters):
                a = sdk2.parameters.String

        class Parameters2(sdk2.Parameters):
            a = sdk2.parameters.String("A")
            with sdk2.parameters.Group("G") as g:
                i = sdk2.parameters.String("I")
            with g:
                j = sdk2.parameters.String("J")

        with pytest.raises(AssertionError):
            class Parameters3(sdk2.Parameters):
                b = Parameters2.a

        class Parameters4(sdk2.Parameters):
            b = Parameters2.a()

        with pytest.raises(AssertionError):
            class Parameters5(Parameters2):
                with Parameters2.g as g:
                    k = sdk2.parameters.String("K")

        with pytest.raises(AssertionError):
            class Parameters6(Parameters2):
                with Parameters2.g:
                    k = sdk2.parameters.String("K")

    def test__parameter_description(self):
        assert sdk2.parameters.Bool().__doc__ == ""
        assert sdk2.parameters.Bool(description=None).__doc__ == ""
        assert sdk2.parameters.Bool(description="foo").__doc__ == "foo"
        assert sdk2.parameters.Bool(description="foo")().__doc__ == "foo"
        assert sdk2.parameters.Bool(description="foo")()()().__doc__ == "foo"
        assert sdk2.parameters.Bool(description="foo")()(description="bar").__doc__ == "bar"

    def test__extend_inherited_groups(self):
        class ParentParams(sdk2.Parameters):
            with sdk2.parameters.Group("Group 1") as group1:
                a = sdk2.parameters.String("A")
            with sdk2.parameters.Group("Group 2") as group2:
                b = sdk2.parameters.String("B")

        class ChildParams(ParentParams):
            with ParentParams.group1() as group1:
                c = sdk2.parameters.String("C")
            with ParentParams.group2() as group2:
                d = sdk2.parameters.String("D")

        assert ParentParams.group1.names == ("a",)
        assert ParentParams.group2.names == ("b",)
        assert ChildParams.group1.names == ("a", "c")
        assert ChildParams.group2.names == ("b", "d")

    # noinspection PyTypeChecker
    def test__remove_inherited_parameters(self):
        class ParentParams(sdk2.Parameters):
            a = sdk2.parameters.String("A")
            b = sdk2.parameters.String("B")
            with sdk2.parameters.Group("G") as g:
                c = sdk2.parameters.String("C")
                d = sdk2.parameters.String("D")

        assert [_.name for _ in ParentParams] == ["a", "b", "g", "c", "d"]
        assert [_.name for _ in ParentParams.g] == ["c", "d"]
        for name in ("a", "b", "c", "d"):
            assert issubclass(getattr(ParentParams, name), sdk2.parameters.String)
            assert getattr(ParentParams, name).name == name
        assert issubclass(ParentParams.g, sdk2.parameters.Group)
        assert ParentParams.g.name == "g"

        class ChildParams(ParentParams):
            a = None
            g = None

        assert [_.name for _ in ChildParams] == ["b"]
        for name in ("a", "g", "c", "d"):
            with pytest.raises(AttributeError):
                getattr(ChildParams, name)
        assert issubclass(ParentParams.b, sdk2.parameters.String)
        assert ParentParams.b.name == "b"

    # noinspection PyUnresolvedReferences,PyTypeChecker,PyArgumentList
    def test__rename_external_parameters(self):
        class ExtParams(sdk2.Parameters):
            a = sdk2.parameters.String("A {a}")
            b = sdk2.parameters.String("B")
            with sdk2.parameters.Group("G {b}") as g:
                c = sdk2.parameters.String("C")
                with c.value["value"]:
                    d = sdk2.parameters.String("D {a} {b}")

        class Params(sdk2.Parameters):
            a = sdk2.parameters.Integer("A")
            ext_params1 = ExtParams(prefix="p_")
            ext_params2 = ExtParams(suffix="_s", label_substs={"a": 123, "b": 321})
            with sdk2.parameters.Group("G") as g:
                c = sdk2.parameters.Integer("C")
            ext_params3 = ExtParams(prefix="p_", suffix="_s")

        with pytest.raises(AssertionError):
            # noinspection PyUnusedLocal
            class WrongSubsts(sdk2.Parameters):
                ext_params1 = ExtParams(label_substs="")

        assert list(Params.g.names) == [_.name for _ in Params.g] == ["c"]
        assert list(ExtParams.g.names) == [_.name for _ in ExtParams.g] == ["c", "d"]
        assert list(Params.p_g.names) == [_.name for _ in Params.p_g] == ["p_c", "p_d"]
        assert list(Params.g_s.names) == [_.name for _ in Params.g_s] == ["c_s", "d_s"]
        assert list(Params.p_g_s.names) == [_.name for _ in Params.p_g_s] == ["p_c_s", "p_d_s"]

        assert Params.p_c.sub_fields == {"value": ("p_d",)}
        assert Params.c_s.sub_fields == {"value": ("d_s",)}
        assert Params.p_c_s.sub_fields == {"value": ("p_d_s",)}

        assert [_.name for _ in Params] == [
            "a",
            "p_a", "p_b", "p_g", "p_c", "p_d",
            "a_s", "b_s", "g_s", "c_s", "d_s",
            "g", "c",
            "p_a_s", "p_b_s", "p_g_s", "p_c_s", "p_d_s",
        ]

        assert [_.description for _ in Params] == [
            "A",
            "A {a}", "B", "G {b}", "C", "D {a} {b}",
            "A 123", "B", "G 321", "C", "D 123 321",
            "G", "C",
            "A {a}", "B", "G {b}", "C", "D {a} {b}",
        ]

        assert [_.name for _ in Params.ext_params1] == ["p_a", "p_b", "p_g", "p_c", "p_d"]
        assert [_.name for _ in Params.ext_params2] == ["a_s", "b_s", "g_s", "c_s", "d_s"]
        assert [_.name for _ in Params.ext_params3] == ["p_a_s", "p_b_s", "p_g_s", "p_c_s", "p_d_s"]

        for name in ("a", "c"):
            assert issubclass(getattr(Params, name), sdk2.parameters.Integer)
            assert getattr(Params, name).name == name
        assert issubclass(Params.g, sdk2.parameters.Group)
        assert Params.g.name == "g"

        for name in (
            "p_a", "p_b", "p_c", "p_d",
            "a_s", "b_s", "c_s", "d_s",
            "p_a_s", "p_b_s", "p_c_s", "p_d_s",
        ):
            assert issubclass(getattr(Params, name), sdk2.parameters.String)
            assert getattr(Params, name).name == name
        for name in ("p_g", "g_s", "p_g_s"):
            assert issubclass(getattr(Params, name), sdk2.parameters.Group)
            assert getattr(Params, name).name == name

    # noinspection PyTypeChecker
    def test__dynamic_parameters(self):
        class Params1(sdk2.Parameters):
            qwer = sdk2.parameters.Bool("Qwer")
            for name in ("c", "b", "a"):
                sdk2.helpers.set_parameter(name, sdk2.parameters.String(name))
            asdf = sdk2.parameters.Bool("Asdf")

        class Params2(sdk2.Parameters):
            asdf = sdk2.parameters.Bool("Asdf")
            for name in ("a", "b", "c"):
                sdk2.helpers.set_parameter(name, sdk2.parameters.String(name))
            qwer = sdk2.parameters.Bool("Qwer")

        class Params3(sdk2.Parameters):
            for name in ("b", "c", "a"):
                sdk2.helpers.set_parameter(name, sdk2.parameters.String(name))
            qwer = sdk2.parameters.Bool("Qwer")
            asdf = sdk2.parameters.Bool("Asdf")

        assert [_.name for _ in Params1] == ["qwer", "asdf", "c", "b", "a"]
        assert [_.name for _ in Params2] == ["asdf", "qwer", "a", "b", "c"]
        assert [_.name for _ in Params3] == ["qwer", "asdf", "b", "c", "a"]

    def test__inherited_output_parameters(self):
        class Params1(sdk2.Parameters):
            qwer = sdk2.parameters.String("Qwer")

        assert Params1.qwer.__output__ is False

        class Params2(sdk2.Parameters):
            with sdk2.parameters.Output:
                subparms = Params1()
                asdf = sdk2.parameters.String("Asdf")

        assert Params1.qwer.__output__ is False
        assert Params2.asdf.__output__ is True
        # noinspection PyUnresolvedReferences
        assert Params2.qwer.__output__ is True
