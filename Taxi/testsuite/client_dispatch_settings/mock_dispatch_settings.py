"""
Usage:

1. add to service.yaml.
Dispatch settings cache must be available before service start

pytest:
    userver-fixture:
      - dispatch_settings_fixture

2. mock
@pytest.mark.dispatch_settings(
    settings=[
        {
          'zone_name': '__default__',
          'tariff_name': '__default__base__',
          'parameters': [
            {
              'values': {'PEDESTRIAN_MAX_SEARCH_RADIUS': 2000000},
            },
          ],
        },
    ],
)

OR

async def awesome_test(
    test_service,
    ...,
    dispatch_settings_mocks,
):
    dispatch_settings_mocks.set_settings(
      settings=[
        {
          'zone_name': '__default__',
          'tariff_name': '__default__base__',
          'parameters': [
            {
              'values': {'PEDESTRIAN_MAX_SEARCH_RADIUS': 2000000},
            },
          ],
        },
      ],
    )
    await test_service.any_handler(url)
    # OR
    await test_service.invalidate_caches()
"""

import pytest

_SERVICE = '/dispatch-settings'
_CATEGORIES_URL = '/v2/categories/fetch'
_SETTINGS_URL = '/v2/settings/fetch'
_DISPATCH_SETTINGS_MARKER = 'dispatch_settings'


class DispatchSettingsContext:
    def __init__(self):
        self._settings = []

    def reset(self):
        self._settings = []

    @property
    def settings(self):
        return self._settings

    def set_settings(self, settings):
        self._settings = settings


def pytest_addoption(parser):
    parser.addini(
        name='mocked-dispatch-settings',
        type='bool',
        default=True,
        help='Set false to disable mocked dispatch-settings by default',
    )


def pytest_configure(config):
    config.addinivalue_line(
        'markers', f'{_DISPATCH_SETTINGS_MARKER}: dispatch settings',
    )


@pytest.fixture(name='dispatch_settings_mocks')
def _dispatch_settings_mocks(mockserver):
    dispatch_settings_context = DispatchSettingsContext()

    @mockserver.json_handler(_SERVICE + _CATEGORIES_URL)
    def _mock_category_fetch(_):
        # feel free to extend or make customizable fixture
        base_group_tariffs = [
            'econom',
            'comfort',
            'business',
            'comfortplus',
            'vip',
            'child_tariff',
            'uberx',
            'uberselect',
            'uberselectplus',
            'uberblack',
            'uberkids',
            'eda',
            'lavka',
            'courier',
            'express',
            'minivan',
            'cargo',
        ]
        return {
            'categories': [
                {
                    'zone_name': '__default__',
                    # not empty tariff_names for sending _SETTINGS_URL request
                    # indeed '__default__base__' isn't necessary here
                    'tariff_names': ['__default__base__'],
                },
            ],
            # `tariff_names` will be fallbacked into __default__base__
            # if there is no settings
            'groups': [
                {'group_name': 'base', 'tariff_names': base_group_tariffs},
            ],
        }

    @mockserver.json_handler(_SERVICE + _SETTINGS_URL)
    def _mock_settings_fetch(_):
        return {'settings': dispatch_settings_context.settings}

    return dispatch_settings_context


@pytest.fixture(name='dispatch_settings_fixture')
def _dispatch_settings_fixture(dispatch_settings_mocks, request):
    marker = request.node.get_closest_marker(_DISPATCH_SETTINGS_MARKER)
    if marker:
        dispatch_settings_mocks.set_settings(**marker.kwargs)

    yield dispatch_settings_mocks

    dispatch_settings_mocks.reset()
