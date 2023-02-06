# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json

import pytest

from contractor_orders_multioffer_plugins import *  # noqa: F403 F401

from tests_contractor_orders_multioffer import mock_candidates


class CandidatesContext:
    def __init__(self):
        self.ids = {
            '4bb5a0018d9641c681c1a854b21ec9ab',
            'e26e1734d70b46edabe993f515eda54e',
            'fc7d65d48edd40f9be1ced0f08c98dcd',
            '47ee2a629f624e6fa07ebd0e159da258',
        }
        self.query = None


@pytest.fixture(name='candidates', autouse=True)
def candidates(mockserver):
    context = CandidatesContext()

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        context.query = request.json
        return {
            'candidates': [
                x
                for x in mock_candidates.CANDIDATES
                if x['uuid'] in context.ids
            ],
        }

    return context


class DoaaContext:
    def __init__(self):
        self.bulk_create_called = 0
        self.bulk_cancel_called = 0
        self.bulk_cancelled_drivers = 0


@pytest.fixture(name='driver_orders_app_api', autouse=True)
def driver_orders_app_api(mockserver):
    context = DoaaContext()

    @mockserver.json_handler(
        '/driver-orders-app-api/internal/v1/order/create_bulk',
    )
    def _v1_order_create_bulk(request):
        context.bulk_create_called += 1
        return {'message': 'some_message'}

    @mockserver.json_handler(
        '/driver-orders-app-api/internal/v2/order/cancel/multioffer',
    )
    def _v2_order_cancel_multioffer(request):
        # sharing the same context simplifies tests
        source = request.path.split('/')[-1]
        assert source == 'multioffer'
        context.bulk_cancel_called += 1
        context.bulk_cancelled_drivers += len(
            request.json['driver_cancel_infos'],
        )
        return {
            'driver_cancel_statuses': [
                {
                    'success': True,
                    'driver': {
                        'park_id': 'some_park_id',
                        'driver_profile_id': 'some_driver_profile_id',
                        'alias_id': 'some_alias_id',
                    },
                },
            ],
        }

    return context


class LookupContext:
    def __init__(self):
        self.event_called_winner = 0
        self.event_called_irrelevant = 0
        self.enriched = []
        self.candidate = None
        self.asserted_event_request = None


@pytest.fixture(name='lookup', autouse=True)
def lookup_mock(mockserver):
    context = LookupContext()

    @mockserver.json_handler('/lookup/event')
    def _event(request):
        assert request.query['lookup_mode'] == 'multioffer'
        if context.asserted_event_request is not None:
            assert request.json == context.asserted_event_request
        if request.json['status'] == 'found':
            context.candidate = request.json['candidate']
            context.event_called_winner += 1
        else:
            context.event_called_irrelevant += 1
        return {'success': True}

    @mockserver.json_handler('/lookup/enrich-candidates')
    def _enrich_candidates(request):
        return {'errors': [], 'candidates': context.enriched}

    return context


class OrderProcContext:
    def __init__(self, load_json):
        self.order_proc = load_json('order_core_response.json')
        self.has_error = False
        self.order_fields_called = 0
        self.set_fields_request_assert = lambda x: True

    def set_response(self, fields, key=None):
        if key:
            self.order_proc['fields'][key].update(fields)
        else:
            self.order_proc['fields'].update(fields)

    def set_error(self):
        self.has_error = True


@pytest.fixture(name='order_proc', autouse=True)
def mock_order_proc(mockserver, load_json):
    context = OrderProcContext(load_json)

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_fields(request):
        context.order_fields_called += 1
        if context.has_error:
            return mockserver.make_response(
                status=500, json={'code': '500', 'message': 'lalala'},
            )
        return context.order_proc

    @mockserver.json_handler('/order-core/v1/tc/set-order-fields')
    def _set_order_fields(request):
        context.set_fields_request_assert(request)
        return mockserver.make_response(status=200, json={})

    return context


class DriverFreezeContext:
    def __init__(self):
        self.defreeze_called = 0
        self.bulk_freeze_called = 0
        self.defreeze_bulk_called = 0
        self.defreeze_response = 200
        self.defreeze_bulk_response = 200
        self.defreeze_bulk_driver_error = None
        self.n_of_request_drivers = 0


@pytest.fixture(name='driver_freeze', autouse=True)
def driver_freeze_mock(mockserver):
    context = DriverFreezeContext()

    @mockserver.json_handler('/driver-freeze/defreeze')
    def _defreeze(request):
        context.defreeze_called += 1
        return mockserver.make_response(status=context.defreeze_response)

    @mockserver.json_handler('/driver-freeze/freeze-bulk')
    def _freeze_bulk(request):
        context.bulk_freeze_called += 1
        return {'drivers': []}

    @mockserver.json_handler('/driver-freeze/defreeze-bulk')
    def _defreeze_bulk(request):
        assert len(request.json['drivers']) == context.n_of_request_drivers
        context.defreeze_bulk_called += 1
        response = {
            'drivers': [
                {
                    'unique_driver_id': 'unique_driver_id',
                    'defreezed': not context.defreeze_bulk_driver_error,
                    'reason': context.defreeze_bulk_driver_error,
                },
            ],
        }
        return mockserver.make_response(
            status=context.defreeze_bulk_response, json=response,
        )

    return context


@pytest.fixture(autouse=True, name='driver_app_profiles')
def driver_app_profile_fixture(mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_get_driver_app(request):
        response = []
        for requested in request.json['id_in_set']:
            response.append(
                {
                    'park_driver_profile_id': requested,
                    'data': {
                        'taximeter_version': '9.50',
                        'taximeter_version_type': '',
                        'taximeter_platform': 'uber',
                    },
                },
            )
        return {'profiles': response}

    return _mock_get_driver_app


@pytest.fixture(name='client_notify', autouse=True)
def client_notify_mock(mockserver):
    @mockserver.json_handler('/client-notify/v2/push')
    def v2_push(request):
        assert request.json['service'] == 'taximeter'
        assert request.json['intent'] == 'MessageNew'
        assert 'client_id' in request.json
        return mockserver.make_response(
            json.dumps({'notification_id': '1488'}), status=200,
        )

    return v2_push
