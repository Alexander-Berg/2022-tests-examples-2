DEFAULT_PRICE = 345
DEFAULT_DEPOT_LOCATION = [10, 20]
DEFAULT_DEPOT_LOCATION_OBJ = {
    'lon': DEFAULT_DEPOT_LOCATION[0],
    'lat': DEFAULT_DEPOT_LOCATION[1],
}
DEFAULT_POSITION = {'location': DEFAULT_DEPOT_LOCATION, 'uri': 'test_url'}
DEFAULT_DEVICE_POSITION = [11, 21]
DEFAULT_ADDITIONAL_DATA = {
    'device_coordinates': {'location': DEFAULT_DEVICE_POSITION},
    'city': 'Moscow',
    'street': 'Bolshie Kamenshiki',
    'house': '8k4',
    'flat': '32',
    'comment': 'test comment',
}
DEFAULT_LEGACY_DEPOT_ID = '0'
DEFAULT_WMS_DEPOT_ID = 'wms_depot_id'
TS_NOW = '2020-03-13T00:50:00+03:00'
TS_DEFAULT_DEPOT_SWITCH_TIME = '2020-03-13T01:00:00+03:00'
CREATED_OFFER_ID = 'created_offer_id'
DEFAULT_VAT = '20.00'
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) '
'Gecko/20100101 Firefox/97.0'
DEFAULT_CURRENCY = 'RUB'

CHECK_REQUEST_ADDITIONAL_DATA = {
    'user_agent': DEFAULT_USER_AGENT,
    'position': DEFAULT_POSITION,
    'currency': DEFAULT_CURRENCY,
    'additional_data': DEFAULT_ADDITIONAL_DATA,
}
