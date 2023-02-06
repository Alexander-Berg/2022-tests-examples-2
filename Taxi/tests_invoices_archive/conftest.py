# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import bson

from invoices_archive_plugins import *  # noqa: F403 F401
from testsuite.utils import matching


class AnonymizedYandexUid(matching.RegexString):
    def __init__(self):
        super().__init__('^-[0-9]{10}$')


def pytest_register_matching_hooks():
    return {
        'bson-objectid': matching.IsInstance(bson.ObjectId),
        'dict': matching.IsInstance(dict),
        'anonymized_puid': AnonymizedYandexUid(),
    }
