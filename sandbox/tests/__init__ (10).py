# coding: utf-8
from __future__ import absolute_import, print_function, unicode_literals

import pytest

from sandbox.common import enum


class Basic(enum.Enum):
    class Group(enum.GroupEnum):
        NUM = None
        DIG = None
        CHR = None

    A = None
    B = "b"
    C = "C"

    with Group.NUM:
        D = 123


Basic.Group.DIG = (Basic.D,)


class Char(enum.Enum):
    class Group(enum.GroupEnum):
        PUNCT = None
        ALPHA = None
        DIGIT = None
        NUMERIC = None

    with Group.PUNCT:
        FULLSTOP = "."

    with Group.ALPHA:
        A = None
        B = None
        C = None

    with Group.DIGIT:
        ONE = 1
        TWO = 2
        THREE = 3


Char.Group.NUMERIC = (Char.ONE, Char.TWO, Char.THREE)


class TestEnums(object):

    def test__basic(self):
        # noinspection PyTypeChecker
        assert set(Basic) == {"A", "b", "C", 123}
        assert Basic.A == "A"
        assert Basic.B == "b"
        assert Basic.C == "C"
        assert Basic.D == 123

    def test__getitem(self):
        assert Basic["A"] == "A"
        assert Basic["B"] == "b"

        with pytest.raises(KeyError):
            Basic["Z"]

    def test__iteritems(self):
        assert set(Basic.iteritems()) == {("A", "A"), ("B", "b"), ("C", "C"), ("D", 123)}

    def test__group_contains(self):
        assert "CHAR" not in Basic.Group
        assert "NUM" in Basic.Group
        assert Basic.Group.NUM in Basic.Group

    def test__group_assign_nonempty(self):
        with pytest.raises(AttributeError):
            Basic.Group.DIG = (Basic.A,)

    def test__group_repr(self):
        assert repr(Basic.Group.NUM) == "NUM"
        assert repr(Basic.Group.DIG) == "DIG"
        assert repr(Basic.Group.CHR) == "CHR"  # empty non-primary groups have separate __repr__

    def test__val2str(self):
        assert Basic.val2str("b") == "B"
        assert Basic.val2str(123) == "D"
        with pytest.raises(ValueError):
            Basic.val2str("z")

    def test__items(self):

        enum.Enum.Item("")  # test default constructor

        class E(enum.Enum):
            class Group(enum.GroupEnum):
                A = enum.GroupEnum.Item()
                B = enum.GroupEnum.Item("group_item_doc")

            with Group.A:
                WITHDOC = enum.Enum.Item("item_doc")
                NODOC = enum.Enum.Item()

            with Group.B:
                AAA = enum.Enum.Item()
                AAB = enum.Enum.Item()

        assert E.WITHDOC.__doc__ == "item_doc"
        assert E.Group.B.__doc__ == "group_item_doc"

        with pytest.raises(AttributeError):
            setattr(E.AAA, "attr", 42)

        with pytest.raises(AttributeError):
            delattr(E.AAA, "attr")

        with pytest.raises(AttributeError):
            setattr(E.Group.A, "attr", 42)

        with pytest.raises(AttributeError):
            delattr(E.Group.A, "attr")

        assert hash(E.AAA) == hash("AAA")
        assert repr(E.AAA) == "AAA"

        assert E.AAA == E.AAA
        assert E.AAA != E.AAB
        assert E.AAA < E.AAB
        assert E.AAB > E.AAA
        assert E.AAA <= E.AAA
        assert E.NODOC >= E.AAA

        assert hash(E.Group.A) == hash("A")
        assert E.Group.A == E.Group.A
        assert E.Group.A != E.Group.B

        assert (E.Group.A + E.Group.B) == (E.Group.A | E.Group.B)
        assert set(E.Group.A + E.Group.B) == set(E.Group.A | E.Group.B)
        assert str(E.Group.A + E.Group.B) == "A+B"

    def test__lower_case(self):
        class E(enum.Enum):
            enum.Enum.lower_case()

            class Group(enum.GroupEnum):
                G = None

            A = None
            B = "B"
            C = "c"

            with Group.G:
                G1 = None
                G2 = "G"
                G3 = "g"

        # noinspection PyTypeChecker
        assert set(E) == {"a", "B", "c", "g1", "G", "g"}
        assert set(E.Group.G) == {"g1", "G", "g"}

    def test__no_underscores(self):

        class E(enum.Enum):
            enum.Enum.no_underscores()
            FOO_BAR = None
            BAR_BUZ = None

        # noinspection PyTypeChecker
        assert set(E) == {"FOOBAR", "BARBUZ"}
        assert E.FOO_BAR == "FOOBAR"

    def test__preserve_order(self):

        class E(enum.Enum):
            enum.Enum.preserve_order()
            Z = None
            Y = None
            X = None
            V = None

        assert list(E) == ["Z", "Y", "X", "V"]
        assert list(E.iteritems()) == [("Z", "Z"), ("Y", "Y"), ("X", "X"), ("V", "V")]

    def test__collapse(self):
        assert Char.Group.collapse(".", 2) == {"PUNCT", 2}
        assert Char.Group.collapse(".", 1, 2, 3) == {"PUNCT", "DIGIT"}
        assert Char.Group.collapse("A", 1) == {"A", 1}
        assert Char.Group.collapse(["A", "B", "C"]) == {"ALPHA"}

    def test__expand(self):
        assert Char.Group.ALPHA.expand() == {"A", "B", "C"}
        assert Char.Group.expand(3) == {3}
        assert Char.Group.expand("ALPHA", 3) == {"A", "B", "C", 3}
        assert Char.Group.expand(Char.Group.DIGIT, Char.FULLSTOP, "A") == {1, 2, 3, ".", "A"}
