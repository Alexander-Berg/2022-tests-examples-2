import pytest
# root conftest for service auto-accept-spawner
pytest_plugins = ['autoaccept_plugins.pytest_plugins']


@pytest.fixture(autouse=True)
def driver_metrics_mock(mockserver):
    @mockserver.handler('/driver-metrics/v1/config/rule/values/')
    def _driver_metrics_mock(_):
        data = {
            'items': [
                {
                    'name': 'CommonDispatchRule',
                    'zone': '__default__',
                    'actions': [
                        {
                            'action': [
                                {
                                    'distance': [1000, 2000],
                                    'time': [86400, 86400],
                                    'type': 'dispatch_length_thresholds',
                                },
                            ],
                        },
                    ],
                },
                {
                    'name': 'CommonDispatchRule',
                    'zone': 'moscow',
                    'actions': [
                        {
                            'action': [
                                {
                                    'distance': [5000, 6000],
                                    'time': [3600, 3600],
                                    'type': 'dispatch_length_thresholds',
                                },
                            ],
                        },
                    ],
                },
            ],
        }
        return mockserver.make_response(json=data, status=200)


@pytest.fixture(name='driver_ui_profile_v1_mode', autouse=True)
def mock_driver_ui_profile_v1_mode(mockserver):
    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_driver_ui_profile_v1_mode(request):
        return mockserver.make_response(
            json={'display_mode': 'taxi', 'display_profile': 'driver'},
            status=200,
        )
