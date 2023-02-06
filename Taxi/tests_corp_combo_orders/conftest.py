# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import dataclasses
import typing

import pytest

from corp_combo_orders_plugins import *  # noqa: F403 F401


@pytest.fixture
def mock_routing_api(mockserver):
    class MockRoutingApi:
        @dataclasses.dataclass
        class RoutingApiData:
            get_mvpr_responses: typing.Optional[typing.Generator]
            response_statuses: typing.Optional[typing.Generator]
            add_mvpr_response: typing.Optional[dict]

        data = RoutingApiData(
            get_mvpr_responses=None,
            response_statuses=None,
            add_mvpr_response=None,
        )

        @staticmethod
        @mockserver.json_handler('/b2bgeo/v1/result/mvrp/routing_task_id_2')
        async def get_mvpr(request):
            return mockserver.make_response(
                json=next(MockRoutingApi.data.get_mvpr_responses),
                status=next(MockRoutingApi.data.response_statuses),
            )

        @staticmethod
        @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
        async def add_mvpr(request):
            return mockserver.make_response(
                json=MockRoutingApi.data.add_mvpr_response, status=202,
            )

    return MockRoutingApi()


@pytest.fixture
def mock_corp_cabinet(mockserver):
    class MockCorpCabinet:
        @dataclasses.dataclass
        class CorpCabinetData:
            cabinet_response_body: typing.Optional[typing.Generator]
            cabinet_response_status: typing.Optional[typing.Generator]
            cabinet_request: typing.Any
            commit_response_body: typing.Dict
            commit_response_status: int

        data = CorpCabinetData(
            cabinet_response_body=None,
            cabinet_response_status=None,
            cabinet_request=None,
            commit_response_body=None,
            commit_response_status=200,
        )

        @staticmethod
        @mockserver.json_handler(
            '/corp-cabinet/internal/1.0/client/client_id_1/order',
        )
        async def create_order_draft(request):
            MockCorpCabinet.data.cabinet_request = request
            return mockserver.make_response(
                json=next(MockCorpCabinet.data.cabinet_response_body),
                status=next(MockCorpCabinet.data.cabinet_response_status),
            )

        @staticmethod
        @mockserver.json_handler(
            r'/corp-cabinet/internal/1.0/order/\w+/processing', regex=True,
        )
        async def commit_order(request):

            return mockserver.make_response(
                json=MockCorpCabinet.data.commit_response_body,
                status=MockCorpCabinet.data.commit_response_status,
            )

    return MockCorpCabinet()


@pytest.fixture
def mock_taxi_tariffs(mockserver):
    class MockTaxiTariffs:
        @dataclasses.dataclass
        class TaxiTariffsData:
            current_tariff_response: dict

        data = TaxiTariffsData(current_tariff_response={})

        @staticmethod
        @mockserver.json_handler('/taxi-tariffs/v1/tariff/current')
        async def get_current_tariff(request):
            return mockserver.make_response(
                json=MockTaxiTariffs.data.current_tariff_response, status=200,
            )

    return MockTaxiTariffs()


@pytest.fixture
def mock_protocol(mockserver):
    class MockProtocol:
        @dataclasses.dataclass
        class ProtocolData:
            nearest_zone_response: dict

        data = ProtocolData(nearest_zone_response={})

        @staticmethod
        @mockserver.json_handler('/protocol/3.0/nearestzone')
        async def get_nearest_zone(request):
            return mockserver.make_response(
                json=MockProtocol.data.nearest_zone_response, status=200,
            )

    return MockProtocol()
