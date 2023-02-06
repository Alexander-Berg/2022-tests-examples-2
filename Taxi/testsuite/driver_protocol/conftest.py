import json

import pytest

from tests_plugins import fastcgi

pytest_plugins = [
    # settings fixture
    'tests_plugins.settings',
    # testsuite plugins
    'taxi_tests.environment.pytest_plugin',
    'taxi_tests.plugins.default',
    'taxi_tests.plugins.aliases',
    'taxi_tests.plugins.translations',
    'taxi_tests.plugins.mocks.configs_service',
    'taxi_tests.plugins.pgsql.deprecated',
    'tests_plugins.daemons.plugins',
    'tests_plugins.testpoint',
    # local mocks
    'tests_plugins.config_service_defaults',
    'tests_plugins.mock_driver_authorizer',
    'tests_plugins.mock_driver_status',
    'tests_plugins.mock_driver_work_rules',
    'tests_plugins.mock_experiments3_proxy',
    'tests_plugins.mock_taxi_exp',
    'tests_plugins.mock_reposition',
    'tests_plugins.mock_driver_tags',
    'tests_plugins.mock_stq',
    'tests_plugins.mock_territories',
    'tests_plugins.mock_tracker',
    'tests_plugins.mock_tvm',
    'tests_plugins.mock_tvm2',
    'tests_plugins.mock_yamaps',
    'tests_plugins.mock_yt',
    'tests_plugins.mock_bss',
    'tests_plugins.mock_geoareas',
    'tests_plugins.mock_agglomerations',
    'tests_plugins.mock_individual_tariffs',
]

taxi_driver_protocol = fastcgi.create_client_fixture('taxi_driver_protocol')


class DMSContext:
    def __init__(self, taxi_config):
        self._use_dms_driver_points = False
        self._expect_dms_called = False
        self._response_driver_points = []
        self._v1_activity_history_response = {'items': []}
        self._response_code = 200
        self._taxi_config = taxi_config

    @property
    def use_dms_driver_points(self):
        return self._use_dms_driver_points

    @property
    def expect_dms_called(self):
        return self._expect_dms_called

    def fetch_driver_points(self, unique_driver_id):
        assert len(self._response_driver_points) > 0
        if isinstance(self._response_driver_points, list):
            return self._response_driver_points.pop(0)
        elif isinstance(self._response_driver_points, dict):
            assert unique_driver_id in self._response_driver_points
            return self._response_driver_points[unique_driver_id]
        else:
            raise Exception('Unsupported testsuite data type in dms_context')

    def set_expect_dms_called(self, expect_dms_called):
        assert isinstance(expect_dms_called, bool)
        self._expect_dms_called = expect_dms_called

    def set_use_dms_driver_points(self, use_dms_driver_points):
        assert isinstance(use_dms_driver_points, bool)
        self._use_dms_driver_points = use_dms_driver_points

    def set_response_driver_points(self, driver_points):
        assert isinstance(driver_points, list) or isinstance(
            driver_points, dict,
        )
        if isinstance(driver_points, dict):
            self._response_driver_points = {
                k: v for k, v in driver_points.items()
            }
        elif isinstance(driver_points, list):
            self._response_driver_points = driver_points[:]
        else:
            raise Exception('Unsupported testsuite data type in dms_context')

    def pick_karma_points(self, dms_activity_value, mongo_driver_points):
        assert dms_activity_value is not None
        assert mongo_driver_points is not None
        if self._use_dms_driver_points:
            return dms_activity_value
        return mongo_driver_points

    def mod_expected_karma_points(self, expected, dms_activity_value):
        assert dms_activity_value is not None
        if not self._use_dms_driver_points:
            return expected
        if isinstance(expected['karma_points'], list):
            for kp in expected['karma_points']:
                kp['value'] = dms_activity_value
        else:
            expected['karma_points']['value'] = dms_activity_value
        return expected

    def set_no_proxy_activity_history_percents(self, percents):
        self._taxi_config.set_values(
            {'ACTIVITY_HISTORY_USING_NO_DM_PROXY': percents},
        )

    def set_v1_activity_history_response(
            self,
            data_or_func,
            response_code: int = 200,
            response_type: str = 'application/json',
    ):
        if isinstance(data_or_func, dict):
            assert 'items' in data_or_func
            assert isinstance(data_or_func['items'], list)
        elif not callable(data_or_func):
            assert isinstance(data_or_func, dict) or callable(data_or_func)
        self._v1_activity_history_response = data_or_func
        self._response_code = response_code
        self._response_type = response_type

    @property
    def v1_activity_history_response(self):
        return self._v1_activity_history_response

    @property
    def response_code(self):
        return self._response_code

    @property
    def response_type(self):
        return self._response_type


@pytest.fixture
def dms_context(taxi_config):
    return DMSContext(taxi_config)


@pytest.fixture
def dms_fixture(mockserver, load_json, dms_context):
    def format_error_response():
        response_body = ''
        if dms_context.response_type == 'application/json':
            response_body = json.dumps(
                {'code': str(dms_context.response_code), 'message': ''},
                ensure_ascii=False,
            )

        return mockserver.make_response(
            response=response_body,
            status=dms_context.response_code,
            content_type=dms_context.response_type,
        )

    @mockserver.json_handler('/driver_metrics_storage/v2/activity_values/list')
    def mock_dms_v2_activity_values_list(request):
        if dms_context.response_code != 200:
            return format_error_response()

        assert dms_context.use_dms_driver_points
        assert dms_context.expect_dms_called
        req = json.loads(request.get_data())
        assert 'strict' not in req
        unique_driver_ids = req['unique_driver_ids']
        assert len(dms_context._response_driver_points) >= len(
            unique_driver_ids,
        )
        return mockserver.make_response(
            response=json.dumps(
                {
                    'items': [
                        {
                            'unique_driver_id': unique_driver_id,
                            'value': dms_context.fetch_driver_points(
                                unique_driver_id,
                            ),
                        }
                        for unique_driver_id in unique_driver_ids
                    ],
                },
                ensure_ascii=False,
            ),
            status=200,
            content_type='application/json',
        )

    @mockserver.json_handler('/driver_metrics_storage/v1/activity/history')
    def mock_dms_v1_activity_history(request):
        if dms_context.response_code != 200:
            return format_error_response()

        req = json.loads(request.get_data())
        assert (
            'event_types' not in req
            or [
                et
                for et in req['event_types']
                if et not in ['dm_service_manual', 'multioffer_order', 'order']
            ]
            == []
        )
        body = json.loads(request.get_data())
        if callable(dms_context.v1_activity_history_response):
            return dms_context.v1_activity_history_response(
                body, event_descriptor_pkey='type',
            )
        return mockserver.make_response(
            status=200,
            content_type='application/json',
            response=json.dumps(
                dms_context.v1_activity_history_response, ensure_ascii=False,
            ),
        )

    class mock_dms:
        def __init__(
                self,
                mock_dms_v2_activity_values_list,
                mock_dms_v1_activity_history,
        ):
            self._v2_activity_values_list = mock_dms_v2_activity_values_list
            self._v1_activity_history = mock_dms_v1_activity_history

        @property
        def v2_activity_values_list(self):
            return self._v2_activity_values_list

        @property
        def v1_activity_history(self):
            return self._v1_activity_history

    return mock_dms(
        mock_dms_v2_activity_values_list, mock_dms_v1_activity_history,
    )


@pytest.fixture
def mock_qc_status(mockserver, load_json):
    @mockserver.json_handler('/qcs/api/v1/state')
    def _mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')


@pytest.fixture
def mock_driver_status(mockserver):
    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}
