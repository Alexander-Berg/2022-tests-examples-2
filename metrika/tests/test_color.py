import pytest

from metrika.pylib.color import colorize


def test_green():
    assert colorize('green', 'green') == '\x1b[92mgreen\x1b[0m'


def test_yellow():
    assert colorize('yellow', 'yellow') == '\x1b[93myellow\x1b[0m'


def test_red():
    assert colorize('red', 'red') == '\x1b[91mred\x1b[0m'


def test_cyan():
    assert colorize('cyan', 'cyan') == '\x1b[36mcyan\x1b[0m'


def test_blue():
    assert colorize('blue', 'blue') == '\x1b[34mblue\x1b[0m'


def test_white():
    assert colorize('white', 'white') == '\x1b[37mwhite\x1b[0m'


def test_black():
    assert colorize('black', 'black') == '\x1b[1;30mblack\x1b[0m'


def test_wrong_color():
    with pytest.raises(ValueError):
        colorize('unknown', 'unknown')
