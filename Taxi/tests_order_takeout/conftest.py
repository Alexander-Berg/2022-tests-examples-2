# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import bson

from order_takeout_plugins import *  # noqa: F403 F401
from testsuite.utils import matching


def pytest_register_matching_hooks():
    return {'bson-objectid': matching.IsInstance(bson.ObjectId)}
