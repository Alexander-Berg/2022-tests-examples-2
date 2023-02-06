import pytest

import metrika.pylib.bstr.config as bstr_config


@pytest.fixture()
def config():
    return bstr_config.BstrConfig(
        var1='a',
        var2=2,
        my_var=True,
        list_var=['asd', 2, '34'],
    )


@pytest.fixture()
def args(config):
    return config.get_args()


def test_args(args):
    assert isinstance(args, list)


def test_simple_arg(args):
    assert '--var1' in args
    assert args[args.index('--var1') + 1] == 'a'


def test_int_arg(args):
    assert '--var2' in args
    assert args[args.index('--var2') + 1] == '2'


def test_long_arg(args):
    assert '--my-var' in args
    assert args[args.index('--my-var') + 1] == 'True'


def test_list_arg(args):
    assert '--list-var' in args
    start = args.index('--list-var')
    assert args[start:start + 6] == ['--list-var', 'asd', '--list-var', '2', '--list-var', '34']


def test_getattr(config):
    assert config.var1 == 'a'
    assert config.var2 == 2
    assert config.no is None
