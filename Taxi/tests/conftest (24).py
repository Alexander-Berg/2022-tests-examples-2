import pytest
from pahtest import config
from pahtest.action import Action
from pahtest.browser import Browser
from pahtest.options import PlainOptions


@pytest.fixture()
def action() -> Action:
    return Action(
        code={'get_ok': '/'}, index=1, options=PlainOptions(name='some action'),
        browser=Browser(name='chrome', hub_url=config.SELENIUM_SERVER),
    )
