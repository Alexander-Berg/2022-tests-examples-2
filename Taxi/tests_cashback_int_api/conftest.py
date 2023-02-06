# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from cashback_int_api_plugins import *  # noqa: F403 F401

from tests_cashback_int_api.utils import requests


@pytest.fixture
def web_cashback_int_api(taxi_cashback_int_api):
    class Ctx:
        def __init__(self, taxi_cashback_int_api):
            self.binding_create = requests.BindingCreate(taxi_cashback_int_api)

    return Ctx(taxi_cashback_int_api)
