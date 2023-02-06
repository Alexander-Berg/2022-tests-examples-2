import functools

import pytest

from discounts_match.adding_rules import *  # noqa: F403 F401
from discounts_match.hierarhies import *  # noqa: F403 F401
from discounts_match.prioritized_entity import *  # noqa: F403 F401
from discounts_match.rules_match import *  # noqa: F403 F401


def required_fixture(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        raise AssertionError(
            f'You need to define fixture with name "{func.__name__}"',
        )

    return wrapper


@pytest.fixture
@required_fixture
def client():
    pass


@pytest.fixture
@required_fixture
def condition_descriptions():
    pass


@pytest.fixture
@required_fixture
def prioritized_entity_url():
    pass


@pytest.fixture
@required_fixture
def add_rules_check_url():
    pass


@pytest.fixture
@required_fixture
def add_rules_url():
    pass


@pytest.fixture
@required_fixture
def default_discount():
    pass


@pytest.fixture
@required_fixture
def headers():
    pass


@pytest.fixture
@required_fixture
def service_name():
    pass


@pytest.fixture
@required_fixture
def hierarchy_descriptions_url():
    pass
