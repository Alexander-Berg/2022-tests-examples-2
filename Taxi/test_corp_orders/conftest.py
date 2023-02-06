# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name

import dataclasses
import typing

import bson
import pytest

import corp_orders.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['corp_orders.generated.service.pytest_plugins']


@pytest.fixture
def simple_secdist(simple_secdist):
    return simple_secdist


@pytest.fixture(autouse=True)
def mock_territories(mockserver):
    @mockserver.json_handler('/territories/v1/countries/list')
    async def _countries(request):
        return {'countries': [{'_id': 'rus', 'vat': 12000}]}

    return _countries


@pytest.fixture
def mock_corp_users(mockserver, load_json):
    def _default_data():
        return {'users': load_json('corp_users.json')}

    class MockCorpUsers:
        @dataclasses.dataclass
        class CorpUsersData:
            users: typing.List[dict]

        data = CorpUsersData(**_default_data())

        @staticmethod
        @mockserver.json_handler('/corp-users/v2/users')
        async def get_user(request):
            user_id = request.query['user_id']

            for user in MockCorpUsers.data.users:
                if user['id'] == user_id:
                    return user

            return mockserver.make_response(
                json={'message': 'User not exists'}, status=404,
            )

    return MockCorpUsers()


@pytest.fixture
def mock_parks_replica(mockserver, load_json):
    class MockParksReplica:
        @dataclasses.dataclass
        class ParksReplicaData:
            parks_data: typing.List[dict]

        data = ParksReplicaData(
            parks_data=load_json('parks_replica_v1_retrieve.json'),
        )

        @staticmethod
        @mockserver.handler('/parks-replica/v1/parks/retrieve')
        def _get_parks_info(request):
            return mockserver.make_response(
                json={
                    'parks': [
                        p
                        for p in MockParksReplica.data.parks_data
                        if p['park_id'] in request.json['id_in_set']
                    ],
                },
            )

    return MockParksReplica()


@pytest.fixture
def mock_parks_activation(mockserver, load_json):
    class MockParksActivation:
        @dataclasses.dataclass
        class ParksActivationData:
            parks_data: typing.List[dict]

        data = ParksActivationData(
            parks_data=load_json('parks_activation_v2_retrieve.json'),
        )

        @staticmethod
        @mockserver.handler('/parks-activation/v2/parks/activation/retrieve')
        def _get_parks_info(request):
            return mockserver.make_response(
                json={
                    'parks_activation': [
                        p
                        for p in MockParksActivation.data.parks_data
                        if p['park_id'] in request.json['ids_in_set']
                    ],
                },
            )

    return MockParksActivation()


@pytest.fixture
def mock_sf_data_load(mockserver):
    class MockSFDataLoad:
        @staticmethod
        @mockserver.handler('/sf-data-load/v1/offer-accept/parks')
        def _offer_accept_parks(request):
            return mockserver.make_response(json={})

    return MockSFDataLoad()


@pytest.fixture
def mock_order_core(mockserver):
    def _get_order_proc(
            procs: typing.List[dict], order_id: str,
    ) -> typing.Optional[dict]:
        for proc in procs:
            if proc['_id'] == order_id:
                return proc
        return None

    class MockOrderCore:
        @dataclasses.dataclass
        class OrderCoreData:
            order_procs: typing.List[dict]
            order_proc_fields: typing.List[str]

        data = OrderCoreData(order_procs=[], order_proc_fields=[])

        @staticmethod
        @mockserver.aiohttp_handler(
            '/order-core/internal/processing/v1/order-proc/get-fields',
        )
        async def order_proc_get_fields(request):
            order_id = request.query['order_id']

            if MockOrderCore.data.order_proc_fields:
                raw_body = await request.read()
                json_body = bson.BSON.decode(raw_body)

                assert json_body == {
                    'fields': MockOrderCore.data.order_proc_fields,
                }

            order_proc = _get_order_proc(
                MockOrderCore.data.order_procs, order_id,
            )

            if not order_proc:
                return mockserver.make_response(
                    json={'error': {'text': 'Not Found'}},
                    content_type='application/json',
                    status=404,
                )

            response = {'document': order_proc}

            return mockserver.make_response(
                bson.BSON.encode(response),
                content_type='application/bson',
                status=200,
            )

    return MockOrderCore()
