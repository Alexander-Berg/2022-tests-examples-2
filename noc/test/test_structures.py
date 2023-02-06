import pytest
from noc.grad.grad.lib.structures import FrozenDict


def test_frozen_dict():
    dic = FrozenDict({"1": 2})
    hash(dic)
    assert "1" in dic
    assert "10" not in dic
    assert FrozenDict.from_rec({"1": {"test": (1, 2)}}) == FrozenDict({'1': FrozenDict({'test': (1, 2)})})
    assert FrozenDict.from_rec({"1": (3, {3: "3"})}) == FrozenDict({"1": (3, FrozenDict({3: "3"}))})

    with pytest.raises(Exception):
        dic = FrozenDict({"1": {"test": []}})  # mutable

    with pytest.raises(Exception):
        dic.clear()

    with pytest.raises(Exception):
        dic.__delitem__("1")

    with pytest.raises(Exception):
        del dic["1"]

    with pytest.raises(Exception):
        dic["2"] = "test"

    with pytest.raises(Exception):
        dic.pop("2")
