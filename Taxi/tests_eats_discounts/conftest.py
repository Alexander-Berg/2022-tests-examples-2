# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from typing import List

import pytest

from eats_discounts_plugins import *  # noqa: F403 F401

from tests_eats_discounts import common


@pytest.fixture
def client(taxi_eats_discounts):
    return taxi_eats_discounts


@pytest.fixture
def headers():
    return common.get_headers()


@pytest.fixture
def service_name():
    return 'eats_discounts'


@pytest.fixture
def add_rules_url():
    return common.ADD_RULES_URL


@pytest.fixture
def add_rules_check_url():
    return common.ADD_RULES_CHECK_URL


@pytest.fixture
def default_discount():
    return common.small_menu_discount()


@pytest.fixture
def condition_descriptions(load_json) -> List[dict]:
    return load_json('hierarchy_descriptions.json')['hierarchies']


@pytest.fixture()
def hierarchy_descriptions_url():
    return '/v1/admin/match-discounts/hierarchy-descriptions'


@pytest.fixture()
def prioritized_entity_url():
    return common.PRIORITIZED_ENTITY_URL


@pytest.fixture()
def priority_check_url():
    return common.PRIORITY_CHECK_URL
