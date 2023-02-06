import pytest

from taxi.util import dictionary

SAMPLE = {
    'foo': {
        'bar': {'baz': 42, 'bazbar': 'str', 'bazbarfoo': [1, 2, 3]},
        'other_key': {'QWE': 'RTY'},
    },
    'qwe': 'rty',
    'foobarbaz': None,
}


@pytest.mark.nofilldb()
def test_root_property():
    result = dictionary.filter(SAMPLE, ['foo'])
    assert result == {'foo': SAMPLE['foo']}


@pytest.mark.nofilldb()
def test_nested_property():
    result = dictionary.filter(
        SAMPLE, ['foo.bar.bazbarfoo', 'foo.other_key', 'invalid_key'],
    )
    assert result == {
        'foo': {
            'bar': {'bazbarfoo': SAMPLE['foo']['bar']['bazbarfoo']},
            'other_key': SAMPLE['foo']['other_key'],
        },
    }


@pytest.mark.nofilldb()
def test_none_property():
    result = dictionary.filter(SAMPLE, ['foobarbaz'])
    assert result == {'foobarbaz': None}
