import pytest

from dmp_suite.descriptors import (
    AttributeDescriptor,
    UngetableAttribute,
    UnsetableAttribute,
    RequiredAttribute,
    UnsupportedAttribute,
)


def test_base_attribute_descriptor():

    class _DummyOne:
        attr_1 = 10
        attr_2 = 20
        attr_3 = AttributeDescriptor("It is alive!")

    assert _DummyOne.attr_3.name == "attr_3"
    assert _DummyOne.attr_3._comment == "It is alive!"

    externally_defined = AttributeDescriptor("And it is too!")
    assert externally_defined.name is None
    assert externally_defined._comment == "And it is too!"

    class _DummyTwo:
        attr_1 = externally_defined
        attr_2 = 10
        attr_3 = "wakeupneo"

    assert _DummyTwo.attr_1.name == "attr_1"
    assert _DummyTwo.attr_1._comment == "And it is too!"

    class _DummyThree:
        def __init__(self):
            self.test_attr = AttributeDescriptor("Bad habit.")

    d3 = _DummyThree()
    assert d3.test_attr.name is None
    assert d3.test_attr._comment == "Bad habit."


def test_ungetable_attribute():

    class _DummyOne:
        attr_1 = 10
        attr_2 = UngetableAttribute("Can't touch this!")

    _DummyOne.attr_1 = 300
    with pytest.raises(AttributeError):
        _ = _DummyOne.attr_2
    with pytest.raises(AttributeError):
        _ = _DummyOne().attr_2
    with pytest.raises(AttributeError):
        print(_DummyOne.attr_2)
    _DummyOne.attr_2 = 500

    externally_defined = UngetableAttribute("While not in class.")
    assert externally_defined.name is None
    assert externally_defined._comment == "While not in class."

    class _DummyTwo:
        attr_1 = externally_defined
        attr_2 = 10
        attr_3 = "followthewhiterabbit"

    with pytest.raises(AttributeError):
        print(_DummyTwo.attr_1.name)
    with pytest.raises(AttributeError):
        print(_DummyTwo().attr_1.name)

    class _DummyThree:
        def __init__(self):
            self.test_attr = UngetableAttribute("Good habit.")

    d3 = _DummyThree()
    assert d3.test_attr.name is None
    assert d3.test_attr._comment == "Good habit."


def test_is_ungetable():

    class A:
        x = UngetableAttribute("???")
        y = 150

    assert not UngetableAttribute.is_ungetable_attribute(A, "y")
    assert not UngetableAttribute.is_ungetable_attribute(A(), "y")
    assert UngetableAttribute.is_ungetable_attribute(A, "x")
    assert UngetableAttribute.is_ungetable_attribute(A(), "x")


def test_unsetable_attribute():

    class _DummyOne:
        attr_1 = 10
        attr_2 = UnsetableAttribute("Will be no other.")

    _DummyOne.attr_1 = 300
    assert _DummyOne.attr_2.name == "attr_2"
    assert _DummyOne().attr_2.name == "attr_2"
    with pytest.raises(AttributeError):
        _DummyOne().attr_2 = 500

    externally_defined = UnsetableAttribute("Just me.")
    assert externally_defined.name is None
    assert externally_defined._comment == "Just me."

    class _DummyTwo:
        attr_1 = externally_defined
        attr_2 = 10
        attr_3 = "followthewhiterabbit"

    assert _DummyTwo.attr_1.name == "attr_1"
    with pytest.raises(AttributeError):
        _DummyTwo().attr_1 = "Not me."

    class _DummyThree:
        def __init__(self):
            self.test_attr = UnsetableAttribute("A habit.")

    d3 = _DummyThree()
    assert d3.test_attr.name is None
    assert d3.test_attr._comment == "A habit."
    d3.test_attr = 'Why not.'


def test_placeholder():

    class _Dummy:
        key = RequiredAttribute("What a place!")

    with pytest.raises(AttributeError):
        _ = _Dummy.key
    with pytest.raises(AttributeError):
        _ = _Dummy().key

    class _DummySuccessor:
        key = 113

    assert _DummySuccessor.key == 113
    assert _DummySuccessor().key == 113

    _Dummy().key = 'big'
    _Dummy.key = 'iron'


def test_unsupported_attribute():

    class _Dummy:
        heart = UnsupportedAttribute("No heart in dummy.")

    with pytest.raises(AttributeError):
        _ = _Dummy.heart
    with pytest.raises(AttributeError):
        _ = _Dummy().heart
    with pytest.raises(AttributeError):
        _Dummy().heart = 'Big heart'
