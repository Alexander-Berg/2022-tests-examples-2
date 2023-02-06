# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest

from corp_suggest_plugins.generated_tests import *

# apply to service test (ping) by default
# pylint: disable=invalid-name
pytestmark = pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED={
        'rus': {'root_geo_node': 'br_russia'},
        'kaz': {'root_geo_node': 'br_kazakhstan'},
    },
)
