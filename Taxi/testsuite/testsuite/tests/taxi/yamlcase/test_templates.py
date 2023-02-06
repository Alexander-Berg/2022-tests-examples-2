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
