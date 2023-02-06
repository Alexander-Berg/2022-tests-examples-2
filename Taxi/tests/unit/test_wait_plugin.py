from pahtest import config
from pahtest.action import Action
from pahtest.browser import Browser
from pahtest.options import PlainOptions


def test_timeout_passing():
    timeout = 2.2
    assert timeout != config.TIMEOUT
    action = Action(
        code=dict(get_ok=dict(url='/', wait=dict(timeout=timeout))),
        index=1, options=PlainOptions(name='some action'),
        browser=Browser(name='chrome', hub_url=config.SELENIUM_SERVER),
    )
    assert timeout == action.wait_plugin.timeout
