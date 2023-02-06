from typing import List

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from logistic_platform_gateway_plugins import *  # noqa: F403 F401


@pytest.fixture(name='get_active_order_ids')
def _active_order_ids(mockserver):
    class Context:
        def __init__(self):
            self.operator_id = None
            self.order_ids = []

        def set_data(self, operator_id: str, order_ids: List[str]):
            self.operator_id = operator_id
            self.order_ids = order_ids

    context = Context()

    @mockserver.json_handler(
        '/logistic-platform-uservices/api/platform/get_active_order_ids',
    )
    def _get_active_order_ids(request):
        assert request.json['operator_id'] == context.operator_id

        return context.__dict__

    return context


@pytest.fixture(name='push_order_event')
def _platform_push_order_event(mockserver):
    class Context:
        def __init__(self):
            self.events = []

        def get_events(self):
            return self.events

    context = Context()

    @mockserver.json_handler(
        '/logistic-platform-uservices/api/platform/accept_gateway_event',
    )
    def _push_order_event(request):
        context.events.append(request.json)

        return {}

    return context


@pytest.fixture(name='lavka_order_events_retrieve')
def _lavka_order_events_retrieve(mockserver):
    class Context:
        def __init__(self):
            self.data = None

        def set_data(self, data: dict):
            self.data = data

    context = Context()

    @mockserver.json_handler(
        '/tristero-b2b/tristero/v1/orders/history/retrieve',
    )
    def _order_events_retrieve(request):
        return context.data

    return context


@pytest.fixture(name='strizh_order_events_retrieve')
def _strizh_order_events_retrieve(mockserver):
    class Context:
        def __init__(self):
            self.data = None

        def set_data(self, data: str):
            self.data = data

    context = Context()

    @mockserver.handler('/strizh/services/v2/sinc.asmx')
    def _order_events_retrieve(request):
        return mockserver.make_response(
            response=context.data,
            headers={'Content-Type': 'application/xml'},
            status=200,
        )

    return context


@pytest.fixture(name='yd_order_events_retrieve')
def _yd_order_events_retrieve(mockserver):
    class Context:
        def __init__(self):
            self.data = None

        def set_data(self, data: dict):
            self.data = data

    context = Context()

    @mockserver.json_handler(r'/yd/orders/[0-9]+/statuses', regex=True)
    def _order_events_retrieve(request):
        return context.data

    return context


@pytest.fixture(name='top_delivery_order_events_retrieve')
def _top_delivery_order_events_retrieve(mockserver):
    class Context:
        def __init__(self):
            self.data = None

        def set_data(self, data: str):
            self.data = data

    context = Context()

    @mockserver.handler('top-delivery/api/soap/h/2.0/')
    def _order_events_retrieve(request):
        return mockserver.make_response(
            response=context.data,
            headers={'Content-Type': 'application/xml'},
            status=200,
        )

    return context
