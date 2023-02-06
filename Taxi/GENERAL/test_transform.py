# pylint: disable=protected-access
from replication_core import transform


def test_castfunction():
    @transform.castfunction
    def cast(value):
        return value * 2

    assert cast._is_castfunction
    assert cast(2) == 4
    assert cast(None) is None


def test_castfunction_pass_none():
    @transform.castfunction(pass_none=True)
    def cast(value):
        return [value]

    assert cast._is_castfunction
    assert cast(2) == [2]
    assert cast(None) == [None]


def test_is_castfunction():
    @transform.castfunction
    def cast(value):
        return None

    assert transform.is_castfunction(cast)


def test_inputtransform():
    @transform.input_transform
    def sample(doc):
        return doc.get('a', 0) + doc.get('b', 0)

    assert sample._is_input_transform
    assert transform.is_input_transform(sample)
