import pytest

from taxi.internal.data_manager import doc_helpers


@pytest.mark.parametrize('doc,path,expected', [
    ({}, 'foo', None),
    ({'foo': 'bar'}, 'foo', 'bar'),
    ({}, 'foo.bar', None),
    ({'foo': '123'}, 'foo.bar', None),
    ({'foo': 123}, 'foo.bar', None),
    ({'foo': []}, 'foo.bar', None),
    ({'foo': {}}, 'foo.bar', None),
    ({'foo': {'bar': 'maurice'}}, 'foo.bar', 'maurice'),
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_get_field_or_none(path, doc, expected):
    result = doc_helpers.get_field_or_none(doc, path)
    assert result == expected


@pytest.mark.parametrize('doc,path,expected', [
    ({}, 'foo', None),
    ({'foo': 'bar'}, 'foo', 'bar'),
    ({}, 'foo.bar', None),
    ({'foo': '123'}, 'foo.bar', None),
    ({'foo': 123}, 'foo.bar', None),
    ({'foo': []}, 'foo.bar', None),
    ({'foo': {}}, 'foo.bar', None),
    ({'foo': {'bar': 'maurice'}}, 'foo.bar', 'maurice'),
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_get_field(path, doc, expected):
    if not expected:
        with pytest.raises(KeyError):
            doc_helpers.get_field(doc, path)
    else:
        result = doc_helpers.get_field(doc, path)
        assert result == expected
