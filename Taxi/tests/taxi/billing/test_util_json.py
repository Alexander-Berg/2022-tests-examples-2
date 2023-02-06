import dataclasses

import pytest

from taxi.billing import util


@dataclasses.dataclass(frozen=True)
class DataclassWithIntField:
    int_value: int


@dataclasses.dataclass(frozen=True)
class DataclassWithDataclassField:
    str_value: str
    dataclass_value: DataclassWithIntField


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'actual,expected',
    [
        (
            DataclassWithDataclassField(
                str_value='foo',
                dataclass_value=DataclassWithIntField(int_value=42),
            ),
            '{"str_value": "foo", "dataclass_value": {"int_value": 42}}',
        ),
        ('str', '"str"'),
    ],
)
def test_to_json(actual, expected):
    assert util.to_json(actual) == expected
