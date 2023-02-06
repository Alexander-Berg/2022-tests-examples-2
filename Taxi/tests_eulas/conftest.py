# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json

from eulas_plugins import *  # noqa: F403 F401
import pytest

from tests_plugins import json_util


class TariffsContext:
    def __init__(self):
        self.payment_options = [
            'card',
            'corp',
            'coupon',
            'applepay',
            'googlepay',
            'personal_wallet',
            'coop_account',
            'cash',
        ]

    def set_payment_options(self, payments):
        self.payment_options = payments


@pytest.fixture(name='taxi_tariffs', autouse=True)
def mock_tariffs(mockserver, load_json):
    context = TariffsContext()

    @mockserver.handler('taxi-tariffs/v1/tariff_settings/bulk_retrieve')
    def _updates(request):
        zone = request.args['zone_names']
        zone_response = {'zone': zone}
        if zone == 'moscow':
            tariff_settings = {
                'country': 'rus',
                'payment_options': context.payment_options,
            }
            zone_response.update({'tariff_settings': tariff_settings})
        else:
            zone_response.update({'status': 'not_found'})

        response = {'zones': [zone_response]}
        return mockserver.make_response(
            json.dumps(response), 200, headers={'X-Polling-Delay-Ms': '100'},
        )

    return context


@pytest.fixture
def service_client_default_headers():
    return {'Accept-Language': 'en'}


@pytest.fixture(name='zones', autouse=True)
def mock_zones_v2_empty(mockserver):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones_v2(request):
        return {'zones': [], 'notification_params': {}}


@pytest.fixture(name='yamaps', autouse=True)
def mock_yamaps_default(mockserver, load_json, yamaps):
    translations = load_json('localizeaddress_config.json')

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        yamaps_vars = None
        locale_translations = translations[request.args['lang']]
        if 'uri' in request.args:
            yamaps_vars = locale_translations[request.args['uri']]
        elif 'll' in request.args:
            yamaps_vars = locale_translations[request.args['ll']]
            yamaps_vars['point'] = request.args['ll']
        return [
            load_json(
                'yamaps_response_default.json',
                object_hook=json_util.VarHook(yamaps_vars),
            ),
        ]
