import pytest

from taxi_testsuite.plugins.yamlcase import templates


@pytest.mark.parametrize(
    'context,obj',
    [
        (
            templates.Context(),
            {'obj': {'foo': 'bar'}, 'list': ['foo', {'foo': 'bar'}]},
        ),
    ],
)
def test_render_same(context, obj):
    result = templates.render(obj, context=context)
    assert result == obj


@pytest.mark.parametrize(
    'context,obj,output',
    [
        # param itself
        (
            templates.Context({'foo': 'bar'}),
            {'foo': {'$param': {'name': 'foo'}}},
            {'foo': 'bar'},
        ),
        (
            templates.Context({'foo': 'bar'}),
            {'foo': [{'$param': {'name': 'foo'}}]},
            {'foo': ['bar']},
        ),
        # nullable
        (
            templates.Context(),
            {'foo': {'$param': {'name': 'foo', 'nullable': True}}},
            {'foo': None},
        ),
        (
            templates.Context(),
            {'foo': [{'$param': {'name': 'foo', 'nullable': True}}]},
            {'foo': [None]},
        ),
        # ifExists
        (
            templates.Context(),
            {'foo': {'$param': {'name': 'foo', 'ifExists': True}}},
            {},
        ),
        (
            templates.Context(),
            {'foo': [{'$param': {'name': 'foo', 'ifExists': True}}]},
            {'foo': []},
        ),
        # default
        (
            templates.Context(),
            {'foo': {'$param': {'name': 'foo', 'default': 'bar'}}},
            {'foo': 'bar'},
        ),
        (
            templates.Context(params={'foo': 'oof'}),
            {'foo': {'$param': {'name': 'foo', 'default': 'bar'}}},
            {'foo': 'oof'},
        ),
    ],
)
def test_param_operators(context, obj, output):
    result = templates.render(obj, context=context)
    assert result == output


def test_matching_disabled():
    with pytest.raises(RuntimeError):
        templates.render(
            {'foo': {'$match': 'any_string'}}, templates.Context(),
        )


@pytest.mark.parametrize(
    'pattern,expected',
    [
        ({'foo': {'$match': 'any-string'}}, {'foo': 'foobar'}),
        (
            {'foo': {'$match': 'uuid-string'}},
            {'foo': 'ea6410555c0343f9ae50294fc3758b8d'},
        ),
        (
            {'foo': {'$match': 'objectid-string'}},
            {'foo': '5e64beab56d0bf70bd8eebbc'},
        ),
        (
            {'foo': {'$match': {'type': 'regex', 'pattern': '^foo.*'}}},
            {'foo': 'foobar'},
        ),
    ],
)
def test_matching_eq(operator_match, pattern, expected):
    result = templates.render(
        pattern,
        templates.Context(operator_match=operator_match),
        allow_matching=True,
    )
    assert result == expected


@pytest.mark.parametrize(
    'pattern,expected',
    [
        ({'foo': {'$match': 'any-string'}}, {'foo': 123}),
        (
            {'foo': {'$match': 'uuid-string'}},
            {'foo': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'},
        ),
        (
            {'foo': {'$match': 'objectid-string'}},
            {'foo': 'XXXXXXXXXXXXXXXXXXXXXXXX'},
        ),
        (
            {'foo': {'$match': {'type': 'regex', 'pattern': '^foo.*'}}},
            {'foo': 'barfoo'},
        ),
    ],
)
def test_matching_neq(operator_match, pattern, expected):
    result = templates.render(
        pattern,
        templates.Context(operator_match=operator_match),
        allow_matching=True,
    )
    assert result != expected
