import json

import pytest


CONFIG_VALUES = {
    'INTEGRATION_SUPPORTED_APPLICATIONS': [
        '/whitelabel/superweb/whitelabel_0',
        '/whitelabel/superweb/whitelabel_1',
        '/whitelabel/turboapp/whitelabel_0',
        '/whitelabel/turboapp/whitelabel_1',
    ],
    'APPLICATION_DETECTION_RULES_NEW': {
        'rules': [
            {
                '@app_name': '/whitelabel/superweb/whitelabel_0',
                'match': '^mozilla/.+whitelabel/superweb/whitelabel_0',
            },
            {
                '@app_name': '/whitelabel/superweb/whitelabel_1',
                'match': '^mozilla/.+whitelabel/superweb/whitelabel_1',
            },
            {
                '@app_name': '/whitelabel/turboapp/whitelabel_0',
                'match': '^mozilla/.+whitelabel/turboapp/whitelabel_0',
            },
            {
                '@app_name': '/whitelabel/turboapp/whitelabel_1',
                'match': '^mozilla/.+whitelabel/turboapp/whitelabel_1',
            },
            {'@app_name': 'web'},
        ],
    },
    'APPLICATION_MAP_BRAND': {
        '__default__': 'yataxi',
        '/whitelabel/superweb/whitelabel_0': '/whitelabel/whitelabel_0',
        '/whitelabel/superweb/whitelabel_1': '/whitelabel/whitelabel_1',
        '/whitelabel/turboapp/whitelabel_0': '/whitelabel/whitelabel_0',
        '/whitelabel/turboapp/whitelabel_1': '/whitelabel/whitelabel_1',
    },
    'INTEGRATION_API_SOURCES_FOR_SAVING_CLIENT_APPLICATION_IN_PROC': [
        'turboapp',
    ],
    'INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID': ['turboapp'],
    'INTEGRATION_API_WHITELABEL_BRANDS': [
        '/whitelabel/whitelabel_0',
        '/whitelabel/whitelabel_1',
    ],
}


@pytest.fixture
def whitelabel_fixtures(config, mockserver):
    config.set_values(CONFIG_VALUES)

    class Context:
        mock_fleet_parks = None

    context = Context()

    @mockserver.json_handler(
        '/fleet_parks/internal/v1/dispatch-requirements/retrieve-by-label',
    )
    def _mock_fleet_parks(request):
        data = json.loads(request.get_data())
        return {
            'label_id': data['label_id'],
            'park_id': 'park_id',
            'dispatch_requirement': 'only_source_park',
        }

    context.mock_fleet_parks = _mock_fleet_parks

    return context
