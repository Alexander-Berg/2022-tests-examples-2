# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import datetime

from overlord_catalog_plugins import *  # noqa: F403 F401
import pytest

from . import overlord_db


NONE_EATS_ID = overlord_db.NONE_EATS_ID


DEFAULT_HEADERS = {
    'X-Request-Application': 'app_name=iphone,app_ver1=10,app_ver2=2',
    'Accept-Language': 'ru-RU',
}

DEFAULT_DEPOT_TIN = '123'


@pytest.fixture(name='mock_grocery_depots')
def mock_grocery_depots(mockserver, load_json):
    class _Mock:
        def __init__(self):
            self.depots = {'depots': [], 'errors': []}
            self.zones = {'zones': []}

            @mockserver.json_handler(
                '/grocery-depots/internal/v1/depots/v1/depots',
            )
            def _handle_depots(_request):
                return self.depots

            @mockserver.json_handler(
                '/grocery-depots/internal/v1/depots/v1/zones',
            )
            def _handle_zones(_request):
                return self.zones

        def setup(self, depots, zones):
            self.depots = depots
            self.zones = zones

        def add_depot(self, depot):
            self.depots['depots'].append(
                {
                    'depot_id': depot.id_wms,
                    'legacy_depot_id': str(depot.depot_id),
                    'country_iso3': depot.country_iso3,
                    'country_iso2': depot.country_iso2,
                    'region_id': depot.region_id,
                    'timezone': depot.timezone,
                    'location': {
                        'lon': depot.location[0],
                        'lat': depot.location[1],
                    },
                    'address': '',  # depot.address,
                    'tin': '',  # depot.tin,
                    'phone_number': '',  # depot.phone_number,
                    'currency': depot.currency or 'RUB',
                    'directions': '',  # depot.directions,
                    'company_type': 'yandex',  # depot.company_type,
                    'name': 'test_' + depot.id_wms,  # depot.name,
                    'short_address': '',  # depot.short_address,
                    'assortment_id': depot.assortment_id,
                    'price_list_id': depot.price_list_id,
                    'root_category_id': depot.root_category.id_wms,
                    'allow_parcels': depot.allow_parcels,
                    'hidden': False,
                    'status': 'active',
                },
            )
            gdepots_zone = []
            for zone in depot.zone['coordinates'][0][0]:
                gdepots_zone.append({'lat': zone[1], 'lon': zone[0]})
            self.zones['zones'].append(
                {
                    'zone_status': 'active',
                    'depot_id': depot.id_wms,
                    'zone_type': 'pedestrian',
                    'zone_id': 'zone_' + depot.id_wms,
                    'geozone': {
                        'type': 'MultiPolygon',
                        'coordinates': [[gdepots_zone]],
                    },
                    'timetable': [
                        {
                            'day_type': 'Everyday',
                            'working_hours': {
                                'from': {'hour': 0, 'minute': 0},
                                'to': {'hour': 24, 'minute': 0},
                            },
                        },
                    ],
                },
            )

        def load_json(
                self,
                depots_filenames,
                zones_filenames,
                replace_at_depots=None,
        ):
            def _suites_depot(depot, props):
                if isinstance(props, (tuple, list)):
                    if depot['legacy_depot_id'] not in props:
                        return False
                else:
                    for key, value in props.items():
                        if key not in depot or depot[key] != value:
                            return False
                return True

            def _make_sure_list(variable):
                return (
                    variable
                    if isinstance(variable, (list, tuple))
                    else [variable]
                )

            depots = []
            zones = []
            for depots_filename in _make_sure_list(depots_filenames):
                depots.extend(load_json(depots_filename)['depots'])
            for zones_filename in _make_sure_list(zones_filenames):
                zones.extend(load_json(zones_filename)['zones'])
            if replace_at_depots:
                replaced = False
                for props, fields in replace_at_depots:
                    for depot in depots:
                        if _suites_depot(depot, props):
                            depot.update(fields)
                            replaced = True
                assert replaced

            self.setup({'depots': depots, 'errors': []}, {'zones': zones})

        def parse_json(self, depots_filename, zones_filename):
            def _parse(value):
                values = value.split()
                # current_timestamp - 1 year
                #   0               1 2 3
                if len(values) > 3 and values[0] == 'current_timestamp':
                    measure = values[3].strip('s') + 's'
                    quantity = int(values[1] + values[2])
                    now = datetime.datetime.now(datetime.timezone.utc)
                    if measure == 'years':
                        now = now.replace(year=now.year + quantity)
                    else:
                        delta = datetime.timedelta(**{measure: quantity})
                        now += delta
                    return now.isoformat()
                return value

            zones = load_json(zones_filename)['zones']
            for zone in zones:
                for key in ['effective_till', 'effective_from']:
                    if key in zone:
                        zone[key] = _parse(zone[key])
            self.setup(load_json(depots_filename), {'zones': zones})

    return _Mock()


@pytest.fixture(name='overlord_db')
def mock_overlord_db(pgsql):
    return overlord_db.OverlordDbAgent(pgsql=pgsql)


@pytest.fixture(name='img_failupload', autouse=True)
def _img_failupload(mockserver):
    @mockserver.handler('/img/.*.jpg', regex=True)
    def _mock_img_failupload(request):
        return mockserver.make_response('<img/>', 200)


@pytest.fixture(name='images_upload', autouse=True)
def _images_upload(mockserver):
    @mockserver.json_handler('/grocery-pics/v2/images/upload')
    def _image_upload(request):
        image_id = '134336879'
        return {
            'id': image_id,
            'path': image_id + '.jpeg',
            'thumbnails_template': image_id + '/{w}x{h}.jpeg',
            'thumbnails': [],
        }


@pytest.fixture(name='mock_sku_images', autouse=True)
def _mock_sku_images(mockserver):
    @mockserver.handler('/lavka/i/sku/.*.jpg', regex=True)
    def _mock_sku_images(request):
        return mockserver.make_response('<img/>', 200)


def wms_empty_response(entity):
    return {'entity': [], 'code': 'OK', 'cursor': 'done'}


@pytest.fixture(name='wms_assortments', autouse=True)
def _wms_assortments(mockserver):
    @mockserver.json_handler('/grocery-wms/api/external/assortments/v1/list')
    def _mock_wms_response(request):
        return wms_empty_response('assortments')


@pytest.fixture(name='wms_assortment_products', autouse=True)
def _wms_assortment_products(mockserver):
    @mockserver.json_handler(
        '/grocery-wms/api/external/assortments/v1/products',
    )
    def _mock_wms_response(request):
        return wms_empty_response('assortment_products')


@pytest.fixture(name='wms_products', autouse=True)
def _wms_products(mockserver):
    @mockserver.json_handler('/grocery-wms/api/external/products/v1/products')
    def _mock_wms_response(request):
        return wms_empty_response('products')


@pytest.fixture(name='wms_product_groups', autouse=True)
def _wms_product_groups(mockserver):
    @mockserver.json_handler('/grocery-wms/api/external/products/v1/groups')
    def _mock_wms_response(request):
        return wms_empty_response('groups')


@pytest.fixture(name='wms_price_lists', autouse=True)
def _wms_price_lists(mockserver):
    @mockserver.json_handler('/grocery-wms/api/external/price_lists/v1/list')
    def _mock_wms_response(request):
        return wms_empty_response('price_lists')


@pytest.fixture(name='wms_price_list_products', autouse=True)
def _wms_price_list_products(mockserver):
    @mockserver.json_handler(
        '/grocery-wms/api/external/price_lists/v1/products',
    )
    def _mock_wms_response(request):
        return wms_empty_response('price_list_products')


@pytest.fixture(name='wms_stocks', autouse=True)
def _wms_stocks(mockserver):
    @mockserver.json_handler('/grocery-wms/api/external/products/v1/stocks')
    def _mock_wms_response(request):
        return wms_empty_response('stocks')


@pytest.fixture(name='wms_stores', autouse=True)
def _wms_stores(mockserver):
    @mockserver.json_handler('/grocery-wms/api/external/stores/v1/list')
    def _mock_wms_response(request):
        return wms_empty_response('stores')


@pytest.fixture(name='wms_companies', autouse=True)
def _wms_companies(mockserver):
    @mockserver.json_handler('/grocery-wms/api/external/companies/v1/list')
    def _mock_wms_response(request):
        return wms_empty_response('companies')


@pytest.fixture(name='grocery_api_surge', autouse=True)
def _grocery_api_surge(mockserver):
    surge_info = {'surge': False, 'delivery_type': 'pedestrian'}

    @mockserver.json_handler('/grocery-api/internal/grocery-api/v2/surge')
    def _mock_wms_response(request):
        result = surge_info.copy()

        if 'place_id' not in result:
            place_ids = request.json['place_ids']
            if place_ids:
                result['place_id'] = place_ids[0]
            else:
                result['place_id'] = '1'

        return {'result': [result]}

    class Context:
        def set_surge_params(
                self,
                place_id=None,
                surge=None,
                minimum_order=None,
                delivery_type=None,
                min_eta_minutes=None,
                max_eta_minutes=None,
        ):
            if place_id is not None:
                surge_info['place_id'] = str(place_id)
            if surge is not None:
                surge_info['surge'] = surge
            if minimum_order is not None:
                surge_info['minimum_order'] = str(minimum_order)
            if delivery_type is not None:
                surge_info['delivery_type'] = delivery_type
            if min_eta_minutes is not None:
                surge_info['min_eta_minutes'] = str(min_eta_minutes)
            if max_eta_minutes is not None:
                surge_info['max_eta_minutes'] = str(max_eta_minutes)

        def flush(self):
            return _mock_wms_response.flush()

        @property
        def times_called(self):
            return _mock_wms_response.times_called

        @property
        def has_calls(self):
            return _mock_wms_response.has_calls

    context = Context()
    return context
