import pytest

from pahtest.browser import Browser
from pahtest.errors import BrowserError


def test_hub_connection():
    defaults = dict(
        name='chrome', width=800, height=600,
        hub_url='http://127.0.0.1:4450/wd/hub'
    )

    # - success and common connect
    b = Browser(**defaults).connect()
    assert b.connected

    # - wrong hub address
    with pytest.raises(BrowserError) as e:
        Browser(
            **{**defaults, 'hub_url': 'http://not-existing/wd/hub'}
        ).connect()
        assert 'Failed to create browser. Wrong selenium hub url.' in str(e)

    # - hub exists, but contains no browser
    with pytest.raises(BrowserError) as e:
        Browser(**{**defaults, 'name': 'firefox'}).connect()
        assert 'Selenium hub contain no driver for firefox.' in str(e)
