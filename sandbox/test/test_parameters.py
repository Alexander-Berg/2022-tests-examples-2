import datetime
import json

import pytest
from six.moves import zip_longest

from sandbox.projects.rope import parameters
from sandbox.projects.rope import toposort
from sandbox.projects.rope.parameters import MISSING


class Mock(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __iter__(self):
        for k, v in self.__dict__.items():
            yield k, v


class MockContext(Mock):
    def save(self):
        pass


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


def test_str_param():
    class TestParams(parameters.TaskParams):
        str_param = parameters.StrParam('Test description')

    assert TestParams.str_param.attr_name == 'str_param'


def test_param_order():

    class BaseTestParams(parameters.TaskParams):
        a = parameters.StrParam('A')
        b = parameters.StrParam('B')
        c = parameters.StrParam('C')

    class CustomTestParams(BaseTestParams):
        aa = parameters.StrParam('AA')
        bb = parameters.StrParam('BB')
        cc = parameters.StrParam('CC')

    class MorePreciseTestParams(CustomTestParams):
        aaa = parameters.StrParam('AAA')
        bbb = parameters.StrParam('BBB')
        ccc = parameters.StrParam('CCC')

    assert [
        parameters.Sdk2ParamCreationData(
            name,
            parameters.sdk2.parameters.String,
            dict(label=name.upper()),
        )
        for name in ['a', 'b', 'c', 'aa', 'bb', 'cc', 'aaa', 'bbb', 'ccc']
    ] == list(MorePreciseTestParams.iter_sdk2_task_specific_param_data())


@pytest.mark.parametrize('value,default,expected_value,expected_dump', [
    (True, None, True, '1'),
    (False, None, False, '0'),
    (None, True, True, '1'),
    (None, False, False, '0'),
    (True, False, True, '1'),
    (False, True, False, '0'),
])
def test_bool_param(value, default, expected_value, expected_dump):

    class TestParams(parameters.TaskParams):
        is_it = parameters.BoolParam('IsIt', required=True,
                                     **dict(default=default) if default is not None else dict())

    mock_params = Mock(is_it=value)
    if default is not None:
        sdk2_param_data = next(TestParams.is_it.iter_sdk2_param_data('is_it'))
        assert default == sdk2_param_data.param_kwargs['default']
        if value is None:
            mock_params.is_it = sdk2_param_data.param_kwargs['default']

    tp = TestParams.from_sdk2_params(mock_params)  # noqa

    assert expected_value == tp.is_it

    assert {'IS_IT': expected_dump} == tp.to_env_args()


@pytest.mark.parametrize('value,expected_error', [
    (u'', ValueError('Empty value is not allowed for param now')),
    (b'', ValueError('Empty value is not allowed for param now')),
    (u'2000.12.31', ValueError('Unsupported date format {!r} for param now'.format(u'2000.12.31'))),
    (b'2000.12.31', ValueError('Unsupported date format {!r} for param now'.format(b'2000.12.31'))),
])
def test_date_param_errors(value, expected_error):

    class TestParams(parameters.TaskParams):
        now = parameters.DateParam('Now', required=True)

    if isinstance(expected_error, type):
        expected_error_class = expected_error
        expected_error_str = None
    else:
        expected_error_class = expected_error.__class__
        expected_error_str = str(expected_error)

    with pytest.raises(expected_error_class) as excinfo:
        TestParams.from_sdk2_params(Mock(now=value))  # noqa

    if expected_error_str:
        assert expected_error_str == str(excinfo.value)


@pytest.mark.parametrize('value,expected_value,expected_dump', [
    (u'2000-12-31', datetime.date(2000, 12, 31), '2000-12-31'),
    (b'2000-12-31', datetime.date(2000, 12, 31), '2000-12-31'),
    (u'978210000',  datetime.date(2000, 12, 31), '2000-12-31'),
    (b'978210000',  datetime.date(2000, 12, 31), '2000-12-31'),
])
def test_date_param(value, expected_value, expected_dump):

    class TestParams(parameters.TaskParams):
        now = parameters.DateParam('Now')

    tp = TestParams.from_sdk2_params(Mock(now=value))  # noqa

    assert expected_value == tp.now

    assert {'NOW': expected_dump} == tp.to_env_args()


@pytest.mark.parametrize('value,expected_error', [
    (u'', ValueError('Empty value is not allowed for param now')),
    (b'', ValueError('Empty value is not allowed for param now')),
    (u'2000.12.31', ValueError('Unsupported datetime format {!r} for param now'.format(u'2000.12.31'))),
    (b'2000.12.31', ValueError('Unsupported datetime format {!r} for param now'.format(b'2000.12.31'))),
])
def test_datetime_param_errors(value, expected_error):

    class TestParams(parameters.TaskParams):
        now = parameters.DateTimeParam('Now', required=True)

    if isinstance(expected_error, type):
        expected_error_class = expected_error
        expected_error_str = None
    else:
        expected_error_class = expected_error.__class__
        expected_error_str = str(expected_error)

    with pytest.raises(expected_error_class) as excinfo:
        TestParams.from_sdk2_params(Mock(now=value))  # noqa

    if expected_error_str:
        assert expected_error_str == str(excinfo.value)


@pytest.mark.parametrize('value,expected_value,expected_dump', [
    (u'2000-12-31', datetime.datetime(2000, 12, 31, tzinfo=parameters.MOSCOW_TZ), '2000-12-31'),
    (b'2000-12-31', datetime.datetime(2000, 12, 31, tzinfo=parameters.MOSCOW_TZ), '2000-12-31'),
    (u'978210000',  datetime.datetime(2000, 12, 31, tzinfo=parameters.MOSCOW_TZ), '2000-12-31'),
    (b'978210000',  datetime.datetime(2000, 12, 31, tzinfo=parameters.MOSCOW_TZ), '2000-12-31'),
    (u'2000-12-31 10', datetime.datetime(2000, 12, 31, 10, tzinfo=parameters.MOSCOW_TZ), '2000-12-31 10:00'),
    (b'2000-12-31T10', datetime.datetime(2000, 12, 31, 10, tzinfo=parameters.MOSCOW_TZ), '2000-12-31 10:00'),
    (u'2000-12-31 10:15', datetime.datetime(2000, 12, 31, 10, 15, tzinfo=parameters.MOSCOW_TZ), '2000-12-31 10:15'),
    (b'2000-12-31T10:15', datetime.datetime(2000, 12, 31, 10, 15, tzinfo=parameters.MOSCOW_TZ), '2000-12-31 10:15'),
    (u'2000-12-31 10:15:37', datetime.datetime(2000, 12, 31, 10, 15, 37, tzinfo=parameters.MOSCOW_TZ), '2000-12-31 10:15:37'),
    (b'2000-12-31T10:15:37', datetime.datetime(2000, 12, 31, 10, 15, 37, tzinfo=parameters.MOSCOW_TZ), '2000-12-31 10:15:37'),
])
def test_datetime_param(value, expected_value, expected_dump):

    class TestParams(parameters.TaskParams):
        now = parameters.DateTimeParam('Now')

    tp = TestParams.from_sdk2_params(Mock(now=value))  # noqa

    assert expected_value == tp.now

    assert {'NOW': expected_dump} == tp.to_env_args()


def test_vault_secret(monkeypatch):
    vault_data_call = []

    def mock_vault_data_call(self, *args, **kwargs):
        vault_data_call.append((args, kwargs))
        return 'secret_foo_token'

    monkeypatch.setattr(parameters.sdk2.Vault, 'data', classmethod(mock_vault_data_call))

    class TestParams(parameters.TaskParams):
        foo_token = parameters.VaultSecretParam('Foo token',
                                                details='OAuth token for Foo service',
                                                default_vault_name='FOO_TOKEN',
                                                default_vault_user='FOO',
                                                specify_owner=True)
    assert [
        parameters.Sdk2ParamCreationData(
            'foo_token_vault_name',
            parameters.sdk2.parameters.String,
            dict(label='Foo token vault name', description='OAuth token for Foo service',
                 required=False, default='FOO_TOKEN'),
        ),
        parameters.Sdk2ParamCreationData(
            'foo_token_vault_user',
            parameters.sdk2.parameters.String,
            dict(label='Foo token vault user', default='FOO'),
        ),
    ] == list(TestParams.iter_sdk2_task_specific_param_data())

    test_params = TestParams.from_sdk2_params(Mock(foo_token_vault_name='FOO_TOKEN',  # noqa
                                                   foo_token_vault_user='FOO'))
    assert len(vault_data_call) > 0
    assert (('FOO', 'FOO_TOKEN'), {}) == vault_data_call.pop()
    assert 'secret_foo_token' == test_params.foo_token

    assert None == TestParams().foo_token  # noqa

    class TestParams(parameters.TaskParams):
        foo_token = parameters.VaultSecretParam('Foo token',
                                                details='OAuth token for Foo service',
                                                default_vault_name='FOO_TOKEN',
                                                default_vault_user='FOO',
                                                specify_owner=False)
    assert [
        parameters.Sdk2ParamCreationData(
            'foo_token_vault_name',
            parameters.sdk2.parameters.String,
            dict(label='Foo token vault name', description='OAuth token for Foo service',
                 default='FOO_TOKEN', required=False),
        ),
    ] == list(TestParams.iter_sdk2_task_specific_param_data())

    test_params = TestParams.from_sdk2_params(Mock(foo_token_vault_name='FOO_TOKEN'))  # noqa
    assert len(vault_data_call) > 0
    assert (('FOO', 'FOO_TOKEN'), {}) == vault_data_call.pop()
    assert 'secret_foo_token' == test_params.foo_token

    class TestParams(parameters.TaskParams):
        foo_token = parameters.VaultSecretParam('Foo token',
                                                details='OAuth token for Foo service',
                                                default_vault_name='FOO_TOKEN',
                                                specify_owner=False)
    assert [
        parameters.Sdk2ParamCreationData(
            'foo_token_vault_name',
            parameters.sdk2.parameters.String,
            dict(label='Foo token vault name', description='OAuth token for Foo service',
                 default='FOO_TOKEN', required=False),
        ),
    ] == list(TestParams.iter_sdk2_task_specific_param_data())

    test_params = TestParams.from_sdk2_params(Mock(foo_token_vault_name='FOO_TOKEN'))  # noqa
    assert len(vault_data_call) > 0
    assert (('FOO_TOKEN', ), {}) == vault_data_call.pop()
    assert 'secret_foo_token' == test_params.foo_token

    class TestParams(parameters.TaskParams):
        foo_token = parameters.VaultSecretParam('Foo token',
                                                details='OAuth token for Foo service',
                                                default_vault_name='FOO_TOKEN',
                                                default_vault_user='FOO',
                                                specify_owner=True,
                                                required=True)
    assert [
        parameters.Sdk2ParamCreationData(
            'foo_token_vault_name',
            parameters.sdk2.parameters.String,
            dict(label='Foo token vault name', description='OAuth token for Foo service',
                 required=True, default='FOO_TOKEN'),
        ),
        parameters.Sdk2ParamCreationData(
            'foo_token_vault_user',
            parameters.sdk2.parameters.String,
            dict(label='Foo token vault user', default='FOO'),
        ),
    ] == list(TestParams.iter_sdk2_task_specific_param_data())

    with pytest.raises(TypeError):
        TestParams()


def test_yav_secret(monkeypatch):
    yav_data_call = []

    def mock_yav_data_call(self, *args, **kwargs):
        yav_data_call.append((args, kwargs))
        return {'foo_token': 'secret_foo_token'}

    monkeypatch.setattr(parameters.sdk2.yav.Secret, 'data', mock_yav_data_call)

    class TestParams(parameters.TaskParams):
        foo_token = parameters.YavSecretParam('Foo token',
                                              details='OAuth token for Foo service',
                                              default_yav_secret='sec-secretFooKey',
                                              default_yav_secret_key='foo_token')
    assert [
        parameters.Sdk2ParamCreationData(
            'foo_token',
            parameters.sdk2.parameters.YavSecret,
            dict(label='Foo token', description='OAuth token for Foo service',
                 default='sec-secretFooKey#foo_token'),
        ),
    ] == list(TestParams.iter_sdk2_task_specific_param_data())

    test_params = TestParams.from_sdk2_params(Mock(  # noqa
        foo_token=parameters.sdk2.yav.Secret(parameters.sdk2.yav.yav.Secret.create(
            'sec-secretFooKey', default_key='foo_token'))
    ))
    assert len(yav_data_call) > 0
    assert (tuple(), {}) == yav_data_call.pop()
    assert 'secret_foo_token' == test_params.foo_token

    assert None == TestParams().foo_token  # noqa


@pytest.mark.parametrize('value,expected_value,expected_dump', [
    (None, None, MISSING),
    (u'', None, MISSING),
    (b'', None, MISSING),
    (u'{"a": "1", "b": "2"}', {'a': '1', 'b': '2'}, '{"a": "1", "b": "2"}'),
    (b'{"a": "1", "b": "2"}', {'a': '1', 'b': '2'}, '{"a": "1", "b": "2"}'),
])
def test_dict_param(value, expected_value, expected_dump):

    class TestParams(parameters.TaskParams):
        params = parameters.DictParam('Params')

    tp = TestParams.from_sdk2_params(Mock(params=value))  # noqa

    assert expected_value == tp.params

    if expected_dump is parameters.MISSING:
        assert {} == tp.to_env_args()
    else:
        assert {'PARAMS': expected_dump} == tp.to_env_args()


@pytest.mark.parametrize('value,expected_error', [
    (MISSING, ValueError),
    (None, ValueError),
    (u'', ValueError),
    (b'', ValueError),
    (u'1', ValueError),
    (b'2', ValueError),
    (u'"asdf"', ValueError),
    (b'"asdf"', ValueError),
    (u'[1, 2]', ValueError),
    (b'[1, 2]', ValueError),
    (u'"asdf"', ValueError),
])
def test_dict_param_errors(value, expected_error):

    class TestParams(parameters.TaskParams):
        params = parameters.DictParam('Params', required=True)

    with pytest.raises(expected_error):
        if value is MISSING:
            TestParams.from_sdk2_params(Mock())  # noqa
        else:
            TestParams.from_sdk2_params(Mock(params=value))  # noqa


@pytest.mark.parametrize('required', [
    True,
    parameters.ParamSrc.ALL,
    parameters.ParamSrc.S | parameters.ParamSrc.C,
    parameters.ParamSrc.S | parameters.ParamSrc.D,
    parameters.ParamSrc.C | parameters.ParamSrc.D,
    parameters.ParamSrc.S,
    parameters.ParamSrc.C,
    parameters.ParamSrc.D,
    parameters.ParamSrc.NONE,
    False,
    None,
])
def test_requirements(required):

    class TestParams(parameters.TaskParams):
        foo = parameters.StrParam('Foo', required=required)

    # Prepare expected
    if isinstance(required, bool) or required is None:
        expected_empty_src = parameters.ParamSrc.NONE if required else parameters.ParamSrc.ALL
    else:
        expected_empty_src = parameters.ParamSrc.ALL ^ required
    expected_error = ValueError
    if expected_empty_src == parameters.ParamSrc.NONE:
        expected_error = TypeError  # More strictly

    if expected_empty_src & parameters.ParamSrc.DIRECTLY_INIT:
        test_params = TestParams()
        assert None == test_params.foo  # noqa
    else:
        with pytest.raises(expected_error):
            TestParams()

    expected_error = ValueError

    if expected_empty_src & parameters.ParamSrc.SANDBOX_SDK2_PARAM:
        test_params = TestParams.from_sdk2_params(Mock())  # noqa
        assert None == test_params.foo  # noqa

        test_params = TestParams.from_sdk2_params(Mock(foo=''))  # noqa
        assert None == test_params.foo  # noqa
    else:
        with pytest.raises(expected_error):
            TestParams.from_sdk2_params(Mock())  # noqa

        with pytest.raises(expected_error):
            TestParams.from_sdk2_params(Mock(foo=''))  # noqa

    if expected_empty_src & parameters.ParamSrc.CLI:
        test_params = TestParams.from_cli_args_or_env(args=[], env={})
        assert None == test_params.foo  # noqa
    else:
        with pytest.raises(expected_error):
            TestParams.from_cli_args_or_env(args=[], env={})


@pytest.mark.parametrize('direct_kwargs,sb_params,cli_args,env,expected_result', [
    (dict(), Mock(), [], {}, None),
    (dict(foo='hello'), Mock(foo='hello'), ['--foo=hello'], {'FOO': 'hello'}, ValueError),
    (dict(foo='bye'), Mock(foo='bye'), ['--foo=bye'], {'FOO': 'bye'}, None),
])
def test_depends_on(direct_kwargs, sb_params, cli_args, env, expected_result):

    class TestParams(parameters.TaskParams):
        foo = parameters.StrParam('Foo')
        bar = parameters.StrParam('Bar', required=True, depend_on=('foo', 'hello'))

    assert [
        parameters.Sdk2ParamCreationData(
            'foo',
            parameters.sdk2.parameters.String,
            dict(label='Foo'),
        ),
        parameters.Sdk2ParamCreationData(
            'bar',
            parameters.sdk2.parameters.String,
            dict(label='Bar', required=True),
            parameters.DependedOn('foo', 'hello')
        ),
    ] == list(TestParams.iter_sdk2_task_specific_param_data())

    if isinstance(expected_result, type) and issubclass(expected_result, Exception):
        with pytest.raises(expected_result):
            TestParams(**direct_kwargs)

        with pytest.raises(expected_result):
            TestParams.from_sdk2_params(sb_params)

        with pytest.raises(expected_result):
            TestParams.from_cli_args_or_env(args=cli_args)

        with pytest.raises(expected_result):
            TestParams.from_cli_args_or_env(args=[], env=env)

        with pytest.raises(expected_result):
            TestParams.from_cli_args_or_env(args=cli_args, env=env)
    else:
        test_params = TestParams(**direct_kwargs)
        assert expected_result == test_params.bar

        test_params = TestParams.from_sdk2_params(sb_params)
        assert expected_result == test_params.bar

        test_params = TestParams.from_cli_args_or_env(args=cli_args)
        assert expected_result == test_params.bar

        test_params = TestParams.from_cli_args_or_env(args=[], env=env)
        assert expected_result == test_params.bar

        test_params = TestParams.from_cli_args_or_env(args=cli_args, env=env)
        assert expected_result == test_params.bar


@pytest.mark.parametrize('default, direct_kwargs,sb_params,cli_args,env,expected_result', [
    (None, dict(), Mock(), [], {}, (TypeError, ValueError)),
    (None, dict(greeting='Hello, World!'), Mock(greeting='Hello, World!'),
     ['--greeting', 'Hello, World!'], {'GREETING': 'Hello, World!'}, 'Hello, World!'),
    ('Hello, World!', dict(), Mock(), [], {}, 'Hello, World!'),
    (lambda p: 'Hello, {}!'.format(getattr(p, 'name', None) or 'World'),
     dict(), Mock(), [], {}, 'Hello, World!'),
    (lambda p: 'Hello, {}!'.format(getattr(p, 'name', None) or 'World'),
     dict(name='Mike'), Mock(name='Mike'), ['--name', 'Mike'], {'NAME': 'Mike'}, 'Hello, Mike!'),
    (parameters.DefaultGetter(lambda p: 'Hello, {}!'.format(p.name), require='name'),
     dict(), Mock(), [], {}, parameters.DefaultGetterRequirementsError),
    (parameters.DefaultGetter(lambda p: 'Hello, {}!'.format(p.name), require='name'),
     dict(name='Steve'), Mock(name='Steve'), ['--name', 'Steve'], {'NAME': 'Steve'}, 'Hello, Steve!'),
])
def test_defaults(default, direct_kwargs, sb_params, cli_args, env, expected_result):

    class TestParams(parameters.TaskParams):
        greeting = parameters.StrParam(
            'Greeting', **dict(default=default, required=True) if default else dict(required=True))
        name = parameters.StrParam('Name')

    def from_sdk2_params():
        mock_context = MockContext()
        test_params = TestParams.from_sdk2_params(sb_params, context=mock_context)  # noqa
        if callable(default):
            assert expected_result == mock_context.greeting  # noqa
            assert is_jsonable(dict(mock_context))
        return test_params

    constructors = [
        lambda: TestParams(**direct_kwargs),
        from_sdk2_params,
        lambda: TestParams.from_cli_args_or_env(args=cli_args),
        lambda: TestParams.from_cli_args_or_env(args=[], env=env),
        lambda: TestParams.from_cli_args_or_env(args=cli_args, env={}),
    ]

    expected_results = expected_result if isinstance(expected_result, tuple) else [expected_result]
    for constructor, expected in zip_longest(constructors, expected_results,
                                             fillvalue=expected_results[-1]):
        if isinstance(expected, type) and issubclass(expected, Exception):
            with pytest.raises(expected):
                constructor()
        else:
            test_params = constructor()
            assert expected == test_params.greeting


def test_complex_defaults():

    class TestParams(parameters.TaskParams):
        full_name = parameters.StrParam(
            'Full name',
            default=parameters.DefaultGetter(lambda p: '{} {}'.format(p.name, p.surname),
                                             require=['name', 'surname']),
        )
        name = parameters.StrParam(
            'Name',
            default=parameters.DefaultGetter(lambda p: p.full_name.split()[0],
                                             require='full_name'),
        )
        surname = parameters.StrParam('Surname')
        greeting = parameters.StrParam(
            'Greeting',
            default=parameters.DefaultGetter(lambda p: 'Hello, {}!'.format(p.name),
                                             require='name'),
        )
        farewell = parameters.StrParam(
            'Farewell',
            default=parameters.DefaultGetter(lambda p: 'Goodbye, {}.'.format(p.name),
                                             require='name'),
        )
        header = parameters.StrParam(
            'Header',
            default=parameters.DefaultGetter(lambda p: '## What Remains of {}'.format(p.full_name),
                                             require='full_name'),
        )

    test_params = TestParams(name='Edith', surname='Finch')
    assert dict(
        full_name='Edith Finch',
        name='Edith',
        surname='Finch',
        greeting='Hello, Edith!',
        farewell='Goodbye, Edith.',
        header='## What Remains of Edith Finch'
    ) == test_params.as_dict()

    test_params = TestParams(full_name='Edith Finch')
    assert dict(
        full_name='Edith Finch',
        name='Edith',
        surname=None,
        greeting='Hello, Edith!',
        farewell='Goodbye, Edith.',
        header='## What Remains of Edith Finch'
    ) == test_params.as_dict()

    with pytest.raises(parameters.DefaultGetterRequirementsError) as exc_info:
        TestParams(name='Edith')
    assert (
        "Requirements ['name'] for default value of full_name param is not satisfied"
    ) == str(exc_info.value)

    with pytest.raises(toposort.CircularDependencyError):
        TestParams()


def test_circular_dependency_in_defaults():

    class TestParams(parameters.TaskParams):
        foo = parameters.StrParam(
            'Foo',
            default=parameters.DefaultGetter(lambda p: p.baz.replace('baz', 'foo'), require='baz'))
        bar = parameters.StrParam(
            'Bar',
            default=parameters.DefaultGetter(lambda p: p.baz.replace('foo', 'bar'), require='foo'))
        baz = parameters.StrParam(
            'Baz',
            default=parameters.DefaultGetter(lambda p: p.baz.replace('bar', 'baz'), require='bar'))

    with pytest.raises(toposort.CircularDependencyError):
        assert dict(a=1) == TestParams().as_dict()


def test_proxy_sandbox_parameters(monkeypatch):
    vault_data_call = []

    def mock_vault_data_call(*args, **kwargs):
        vault_data_call.append((args, kwargs))
        return 'secret_foo_token'

    monkeypatch.setattr(parameters.sdk2.Vault, 'data', classmethod(mock_vault_data_call))

    yav_data_call = []

    def mock_yav_data_call(self, *args, **kwargs):
        yav_data_call.append((args, kwargs))
        return {'new_bar_token': 'secret_bar_token'}

    monkeypatch.setattr(parameters.sdk2.yav.Secret, 'data', mock_yav_data_call)

    class TestParams(parameters.TaskParams):
        foo = parameters.StrParam(
            'Foo',
            default=lambda p: 'foo',
        )
        bar = parameters.StrParam(
            'bar',
            default=lambda p: 'bar',
        )
        foo_token = parameters.VaultSecretParam(
            'Foo token',
            details='OAuth token for Foo service',
            default_vault_name='FOO_TOKEN',
            default_vault_user='FOO',
            specify_owner=True,
            required=True,
        )
        bar_token = parameters.YavSecretParam(
            'Bar token',
            default_yav_secret='sec-secretBasKey',
            default_yav_secret_key='bar_token',
        )
        baz = parameters.StrParam(
            'Baz',
            skip_in=parameters.ParamSrc.SANDBOX_SDK2_PARAM,
            default=lambda p: 'baz',
        )
        qux = parameters.StrParam(
            'Qux',
            load_from_sdk2_params=lambda value: value.upper(),
            sdk2_param_proxy=lambda value, name_n_param: {name_n_param[0]: name_n_param[1]}
        )

    mock_params = Mock(
        foo=None,
        prefix_bar=None,
        prefix_foo_token_vault_name='NEW_FOO_TOKEN',
        prefix_foo_token_vault_user='ME',
        bar_token=parameters.sdk2.yav.Secret(parameters.sdk2.yav.yav.Secret.create(
            'sec-secretBasKey', default_key='new_bar_token')),
        qux='qux',
    )
    mock_context = MockContext()
    test_params = TestParams.from_sdk2_params(mock_params, prefix='prefix_', context=mock_context)  # noqa

    assert dict(
        foo='foo',
        bar='bar',
        foo_token='secret_foo_token',
        bar_token='secret_bar_token',
        baz='baz',
        qux='QUX'
    ) == test_params.as_dict()

    assert dict(
        foo='foo',
        prefix_bar='bar',
        prefix_foo_token_vault_name='NEW_FOO_TOKEN',
        prefix_foo_token_vault_user='ME',
        bar_token='sec-secretBasKey#new_bar_token',
        qux='qux'
    ) == test_params.proxy_sandbox_params(mock_params, prefix='prefix_')  # noqa

    mock_context_dict = dict(mock_context)
    assert is_jsonable(mock_context_dict)
    assert {'foo', 'prefix_bar'} == set(mock_context_dict.pop('__calculated_defaults__'))
    assert {
        'foo': 'foo',
        'prefix_bar': 'bar',
    } == mock_context_dict


def test_calculated_default_dump():

    class TestParams(parameters.TaskParams):
        now = parameters.DateTimeParam('Now', default=lambda p: datetime.datetime(2000, 12, 31))
        name_to_ages = parameters.DictParam('Name to ages', default=lambda p: {'John': '27'})

    mock_context = MockContext()
    tp = TestParams.from_sdk2_params(Mock(), context=mock_context)  # noqa

    mock_context_dict = dict(mock_context)
    assert is_jsonable(mock_context_dict)
    assert {'now', 'name_to_ages'} == set(mock_context_dict.pop('__calculated_defaults__'))
    assert {
        'now': '2000-12-31',
        'name_to_ages': {'John': '27'},
    } == mock_context_dict
