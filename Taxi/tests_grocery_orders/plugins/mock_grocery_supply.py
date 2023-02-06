import random

import pytest

COURIER_INFO = 'courier-info-handler'
COURIER_SERVICE_INFO = 'courier-service-info-handler'

COURIER_SERVICE = {
    'courier_service_id': 1453,
    'name': 'Yandex',
    'address': '123 street',
    'ogrn': '12345',
    'work_schedule': '8:00-19:00',
    'inn': '1234',
    'vat': 20,
}

COURIER = {
    'courier_id': '1337',
    'driver_id': 'driver_uuid',
    'full_name': 'Anton Antonov',
    'transport_type': 'rover',
    'courier_service': COURIER_SERVICE,
    'phone': 'phone_id_1',
    'inn': 'inn_id_1',
    'balance_client_id': '123',
}


@pytest.fixture(name='grocery_supply')
def mock_grocery_supply(mockserver):
    class Context:
        def __init__(self):
            self.courier = COURIER
            self.error_code = {}
            self.check_courier_data = None
            self.check_courier_service_data = None
            self.courier_response = None
            self.courier_service_response = None
            self.log_group_mapping = {}

        def check_courier_info(self, **argv):
            self.check_courier_data = {}
            for key in argv:
                self.check_courier_data[key] = argv[key]

        def check_courier_service_info(self, **argv):
            self.check_courier_service_data = {}
            for key in argv:
                self.check_courier_service_data[key] = argv[key]

        def set_courier_response(self, response):
            self.courier_response = response

        def set_courier_service_response(self, response):
            self.courier_service_response = response

        def set_error_code(self, handler, code):
            self.error_code[handler] = code

        def add_log_group(self, depot_id, log_group_id):
            self.log_group_mapping[depot_id] = log_group_id
            return self.log_group_mapping

        def gen_log_group(self, depot_id):
            log_group_id = str(random.randint(0, 10000))
            self.add_log_group(depot_id, log_group_id)
            return log_group_id

        def times_courier_called(self):
            return mock_courier_info.times_called

        def times_courier_service_called(self):
            return mock_courier_service_info.times_called

        def times_get_log_group_called(self):
            return mock_get_log_group.times_called

        def flush_all(self):
            mock_courier_info.flush()

    context = Context()

    @mockserver.json_handler(
        '/grocery-supply/internal/v1/supply/v1/courier/info',
    )
    def mock_courier_info(request):
        if COURIER_INFO in context.error_code:
            code = context.error_code[COURIER_INFO]
            return mockserver.make_response(
                '{"message": "bad request", "code": "bad_request"}',
                status=code,
            )

        if context.check_courier_data is not None:
            for key, value in context.check_courier_data.items():
                assert request.json[key] == value, key

        if context.courier_response is not None:
            return context.courier_response

        response = context.courier
        response['courier_id'] = request.json['courier_id']
        return response

    @mockserver.json_handler(
        '/grocery-supply/internal/v1/supply/v1/courier-service/info',
    )
    def mock_courier_service_info(request):
        if COURIER_SERVICE_INFO in context.error_code:
            code = context.error_code[COURIER_SERVICE_INFO]
            return mockserver.make_response(
                '{"message": "bad request", "code": "bad_request"}',
                status=code,
            )

        if context.check_courier_service_data is not None:
            for key, value in context.check_courier_service_data.items():
                assert request.json[key] == value, key

        if context.courier_service_response is not None:
            return context.courier_service_response

        return {
            'courier_service': {
                'name': 'ООО ЛКП',
                'courier_service_id': int(request.json['courier_service_id']),
                'tin': '1234',
            },
        }

    @mockserver.json_handler(
        '/grocery-supply/internal/v1/supply/v1/get_log_group',
    )
    def mock_get_log_group(request):
        log_group_id = context.log_group_mapping.get(request.json['depot_id'])
        if log_group_id is None:
            return mockserver.make_response(json={}, status=404)

        return {'log_group_id': log_group_id}

    return context
