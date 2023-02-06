# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from driver_mode_subscription_plugins import *  # noqa: F403 F401
import pytest

from tests_driver_mode_subscription import mode_rules


@pytest.fixture
def taxi_dms_mock(mockserver):
    class Mocks:
        expect_times_called = 0
        last_called_tags = 'none'
        last_extra_data = 'none'

        @staticmethod
        @mockserver.json_handler('/driver-metrics-storage/v2/event/new')
        def _event_new(request):
            Mocks.expect_times_called += 1
            if 'tags' in request.json['descriptor']:
                Mocks.last_called_tags = request.json['descriptor']['tags']
            if 'extra_data' in request.json:
                Mocks.last_extra_data = request.json['extra_data']
            return {}

    return Mocks()


# Usage: @pytest.mark.mode_rules(
#            patches=List[mode_rules.Patch] = [],
#            rules: Optional[Dict[str, List[Dict[str, Any]]]] = None
#        )
_MODE_RULES_MARKER = 'mode_rules'
_DB_SERVICE_NAME = 'driver_mode_subscription'


class ModeRuleContext:
    def __init__(self, taxi_config, pgsql):
        self.taxi_config = taxi_config
        self.pgsql = pgsql

    def reset(self):
        pass

    def set_mode_rules(self, patches=None, rules=None):
        if patches is None:
            patches = []

        cursor = self.pgsql[_DB_SERVICE_NAME].cursor()
        cursor.execute(mode_rules.patched_db(patches=patches, rules=rules))


@pytest.fixture(name='mode_rules_data')
def _mode_rules_fixture(taxi_config, pgsql, request):
    mode_rules_context = ModeRuleContext(taxi_config, pgsql)
    # TODO: get_closest_marker not work with mark in parametrize
    # example: test_mode_set_validation_reposition.py
    # marker = request.node.get_closest_marker(_MODE_RULES_MARKER)
    marker = None
    for marker in request.node.iter_markers(_MODE_RULES_MARKER):
        pass

    if marker:
        mode_rules_context.set_mode_rules(**marker.kwargs)

    return mode_rules_context


class ModeGeographyContext:
    def __init__(self, taxi_config, pgsql):
        self.taxi_config = taxi_config
        self.pgsql = pgsql

    def reset(self):
        pass

    def set_defaults(
            self,
            work_modes_always_available=None,
            work_modes_available_by_default=None,
    ):
        always_available = (
            work_modes_always_available if work_modes_always_available else []
        )
        available_by_defaul = (
            work_modes_available_by_default
            if work_modes_available_by_default
            else []
        )
        self.taxi_config.set_values(
            {
                'DRIVER_MODE_GEOGRAPHY_DEFAULTS': {
                    'work_modes_always_available': always_available,
                    'work_modes_available_by_default': available_by_defaul,
                },
            },
        )

    def set_all_modes_available(self):
        cursor = self.pgsql['driver_mode_subscription'].cursor()
        cursor.execute('SELECT config.modes.name FROM config.modes')
        rows = list(row[0] for row in cursor)

        self.set_defaults(work_modes_always_available=rows)


@pytest.fixture(name='mode_geography_defaults')
def _mode_geography_fixture(mode_rules_data, taxi_config, pgsql, request):
    mode_geography_context = ModeGeographyContext(taxi_config, pgsql)
    mode_geography_context.set_all_modes_available()
    return mode_geography_context


def pytest_configure(config):
    config.addinivalue_line('markers', f'{_MODE_RULES_MARKER}: set mode rules')
