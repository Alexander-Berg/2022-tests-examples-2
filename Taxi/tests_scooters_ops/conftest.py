import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from scooters_ops_plugins import *  # noqa: F403 F401


JSON_PERFORMER_RESULT = {
    'car_id': 'car_id1',
    'car_model': 'some_car_model',
    'car_number': 'some_car_number',
    'driver_id': 'driver_id1',
    'lookup_version': 1,
    'name': 'Kostya',
    'order_alias_id': '1234',
    'order_id': '9db1622e-582d-4091-b6fc-4cb2ffdc12c0',
    'park_clid': 'park_clid1',
    'park_id': 'park_id1',
    'park_name': 'some_park_name',
    'park_org_name': 'some_park_org_name',
    'phone_pd_id': 'phone_pd_id',
    'revision': 1,
    'tariff_class': 'cargo',
    'transport_type': 'electric_bicycle',
}


@pytest.fixture(name='cargo_orders')
def _cargo_orders(mockserver, load_json):
    class CargoOrdersContext:
        def __init__(self):
            self.waybill = load_json('default_waybill.json')
            self.current_point_id = 1

        def set_waybill(self, load_json, waybill_path, current_point_id=None):
            self.waybill = load_json(waybill_path)
            self.current_point_id = current_point_id or self.current_point_id
            self.waybill['execution']['points'][self.current_point_id][
                'is_resolved'
            ] = False

        def resolve_current_point_and_move(self):
            self.waybill['execution']['points'][self.current_point_id][
                'is_resolved'
            ] = True
            self.current_point_id += 1

    context = CargoOrdersContext()

    @mockserver.json_handler('/cargo-orders/v1/pro-platform/order-info')
    def _get_order_info(request):
        return {'performer': JSON_PERFORMER_RESULT, 'waybill': context.waybill}

    @mockserver.json_handler('/cargo-orders/v1/pro-platform/arrive_at_point')
    def _arrive_at_point(request):
        return {'performer': JSON_PERFORMER_RESULT, 'waybill': context.waybill}

    @mockserver.json_handler('/cargo-orders/v1/pro-platform/exchange/confirm')
    def _exchange_confirm(request):
        context.resolve_current_point_and_move()
        return {'performer': JSON_PERFORMER_RESULT, 'waybill': context.waybill}

    setattr(context, 'get_order_info', _get_order_info)
    setattr(context, 'arrive_at_point', _arrive_at_point)
    setattr(context, 'exchange_confirm', _exchange_confirm)
    return context


@pytest.fixture(name='driver_trackstory')
def _driver_trackstory(mockserver):
    class DriverTrackstoryContext:
        def __init__(self):
            self.lat = 55.1
            self.lon = 37.1
            self.speed = 0.0
            self.accuracy = 1.0
            self.timestamp = 1651240098
            self.driver_id = 'performer_1'

        def set_lat(self, lat):
            self.lat = lat

        def set_lon(self, lon):
            self.lon = lon

        def set_speed(self, speed):
            self.speed = speed

        def set_accuracy(self, accuracy):
            self.accuracy = accuracy

        def set_timestamp(self, timestamp):
            self.timestamp = timestamp

        def set_driver_id(self, driver_id):
            self.driver_id = driver_id

    context = DriverTrackstoryContext()

    @mockserver.json_handler('/driver-trackstory/position')
    async def _driver_position(request):
        assert request.json == {'driver_id': context.driver_id}
        return {
            'position': {
                'lat': context.lat,
                'lon': context.lon,
                'speed': context.speed,
                'accuracy': context.accuracy,
                'timestamp': context.timestamp,
            },
            'type': 'raw',
        }

    setattr(context, 'driver_position', _driver_position)
    return context
