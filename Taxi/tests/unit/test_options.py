import pytest
import yaml

from pahtest import config
from pahtest.file import File
from pahtest.errors import PahtestError
from pahtest.options import Commands, OptionsSet, PlainOptions


def test_options_set_validation():
    # - success
    opts = OptionsSet(
        code={'base_url': 'http://nginx', 'browser': 'chrome'}, name='test'
    ).validate()
    assert opts._dict

    # - wrong type
    with pytest.raises(PahtestError) as e:
        # noinspection PyTypeChecker
        OptionsSet(
            code=[{'base_url': 'http://nginx', 'browser': 'chrome'}],
            name='test'
        ).validate()
        assert 'options set must have dict type' in str(e)

    # - success with list
    opts = OptionsSet(
        code={'base_url': 'http://nginx', 'list': [
            {'browser': 'chrome'}, {'browser': 'firefox'},
        ]}, name='test'
    ).validate()
    assert opts._dict

    # - wrong type
    with pytest.raises(PahtestError) as e:
        OptionsSet(
            code={'base_url': 'http://nginx', 'list': {'browser': 'chrome'}},
            name='test'
        ).validate()
        assert 'options.list field\'s wrong type' in str(e)


def test_plain_options_validation():
    # - success with list
    opts = PlainOptions(code={'base_url': 'http://nginx'}, name='test')
    opts.validate()
    assert opts.dict

    # - wrong type
    with pytest.raises(PahtestError) as e:
        PlainOptions(
            code={'width': 'wrong type'}, name='test'
        ).validate().normalize()
        assert 'Failed to cast' in str(e)


def test_plain_options_merge():
    # - hoisted cli
    opts = PlainOptions(
        name='test', code={'browser': 'chrome'}, cli={'browser': 'firefox'}
    )
    opts.normalize()
    assert 'firefox' == opts.dict['browser']
    # - hoisted defaults
    opts = PlainOptions(code={}, name='test').normalize()
    assert config.SELENIUM_SERVER == opts.dict['selenium_hub_url']


def test_options_normalize():
    # - failed to cast
    with pytest.raises(PahtestError) as e:
        PlainOptions(code={'width': 'not a num'}, name='test').normalize()
        assert 'Failed to cast' in str(e)

    # - wrong height value
    with pytest.raises(PahtestError) as e:
        PlainOptions(code={'height': -1}, name='test').normalize()
        assert 'With must be in range' in str(e)

    # - wrong browser
    with pytest.raises(PahtestError) as e:
        PlainOptions(code={'browser': 'exotic'}, name='test').normalize()
        assert 'Browser exotic is not supported' in str(e)

    # - defaults options are created
    opts = PlainOptions(code={}, name='test')
    expected = {
        'width', 'height', 'browser', 'selenium_hub_url',
        'timeout', 'waiting_step',
    }
    assert expected == set(opts.normalize().dict.keys())

    # - hoisted cli
    opts = OptionsSet(
        code={'browser': 'chrome'}, cli={'browser': 'firefox'}, name='test'
    )
    opts.normalize()
    assert 'firefox' == opts._dict['browser']
    # - hoisted defaults
    opts = OptionsSet(code={}, name='test').normalize()
    assert config.SELENIUM_SERVER == opts._dict['selenium_hub_url']

    # - default value
    opts = OptionsSet(
        code={'base_url': 'http://nginx', 'browser': 'chrome'}, name='test'
    ).normalize()
    assert 'timeout' in opts._dict
    assert config.TIMEOUT == opts._dict['timeout']


def test_options_passing():
    step = 0.3

    # - pass waiting_step with cli options
    file = File(
        name='Options', path='file_for_options.yml',
        cli_options=dict(waiting_step=step),
        code=dict(options=dict(browser='chrome'), tests=dict(get_ok='/'))
    )
    # file -> case.actions -> action
    action = file.subtests[0].actions.subtests[0]
    assert step == action.waiting_step

    # - pass waiting_step with options yaml section
    file = File(
        name='Options', path='file_for_options.yml',
        code=dict(
            options=dict(browser='chrome', waiting_step=step),
            tests=dict(get_ok='/')
        ),
    )
    # file -> case.actions -> action
    action = file.subtests[0].actions.subtests[0]
    assert step == action.waiting_step


def test_command_validation():
    # - success
    cmd = Commands(yaml.load(
        'create_user:'
        '\n  code: curl http://foo.bar.baz'
        '\n  format: sh'
        , Loader=yaml.FullLoader
    ))
    cmd.validate()

    # - empty commands is appreciated
    cmd = Commands({})
    cmd.validate()

    # - missed "format" field
    cmd = Commands(yaml.load(
        'create_user:\n'
        '\n  code: curl http://foo.bar.baz'
        , Loader=yaml.FullLoader
    ))
    with pytest.raises(PahtestError) as e:
        cmd.validate()
        assert 'Missed fields' in str(e)

    # - unwanted "wrong" field
    cmd = Commands(yaml.load(
        'create_user:'
        '\n  code: curl http://foo.bar.baz'
        '\n  wrong: foo.bar.baz'
        , Loader=yaml.FullLoader
    ))
    with pytest.raises(PahtestError) as e:
        cmd.validate()
        assert 'Unwanted fields' in str(e)

    # - good "format" field
    cmd = Commands(yaml.load(
        'create_user:'
        '\n  code: curl http://foo.bar.baz'
        '\n  format: sh'
        , Loader=yaml.FullLoader
    ))
    cmd.validate()

    # - bad "format" field
    cmd = Commands(yaml.load(
        'create_user:'
        '\n  code: curl http://foo.bar.baz'
        '\n  format: wrong'
        , Loader=yaml.FullLoader
    ))
    with pytest.raises(PahtestError) as e:
        cmd.validate()
        assert 'Unknown format' in str(e)

    # - good "format" field with dict
    cmd = Commands(yaml.load(
        'create_user:'
        '\n  code: curl http://foo.bar.baz'
        '\n  format:'
        '\n    input: none'
        '\n    output: sh'
        , Loader=yaml.FullLoader
    ))
    cmd.validate()

    # - input with type "sh" should fail
    cmd = Commands(yaml.load(
        'create_user:'
        '\n  code: curl http://foo.bar.baz'
        '\n  format:'
        '\n    input: sh'
        '\n    output: none'
        , Loader=yaml.FullLoader
    ))
    with pytest.raises(PahtestError) as e:
        cmd.validate()
        assert 'Shell input format is not supported' in str(e)
