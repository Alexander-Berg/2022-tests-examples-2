# pylint: disable=redefined-outer-name
import dataclasses
from typing import Any

from aiohttp import web
import pytest

import contractor_permits.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['contractor_permits.generated.service.pytest_plugins']


@dataclasses.dataclass
class DriverProfilesContext:
    handler: Any = None


@pytest.fixture
async def mock_driver_profiles_ctx(mock_driver_profiles):
    ctx = DriverProfilesContext()

    @mock_driver_profiles('/v1/driver/profiles/retrieve_by_park_id')
    async def mocked_dp_handler(request):
        assert request.json['park_id_in_set'] == ['dbid1']
        assert sorted(request.json['projection']) == sorted(
            ['data.car_id', 'data.full_name', 'data.license.pd_id'],
        )
        return web.json_response(
            {
                'profiles_by_park_id': [
                    {
                        'park_id': 'dbid1',
                        'profiles': [
                            # OK - white-plated car
                            {
                                'data': {
                                    'car_id': 'car_id_1',
                                    'license': {'pd_id': 'pd_id_1'},
                                    'full_name': {
                                        'first_name': 'VJAČESLAVS',
                                        'last_name': 'JEMEĻJANOVS',
                                        'middle_name': 'Tv-1',
                                    },
                                },
                                'park_driver_profile_id': 'dbid1_uuid1',
                            },
                            # Driver permit expired
                            {
                                'data': {
                                    'car_id': 'car_id_2',
                                    'license': {'pd_id': 'pd_id_2'},
                                    'full_name': {
                                        'first_name': 'VJAČESLAVS',
                                        'last_name': 'JEMEĻJANOVS',
                                        'middle_name': 'TV-2 ',
                                    },
                                },
                                'park_driver_profile_id': 'dbid1_uuid2',
                            },
                            # Car permit expired
                            {
                                'data': {
                                    'car_id': 'car_id_3',
                                    'license': {'pd_id': 'pd_id_3'},
                                    'full_name': {
                                        'first_name': 'VJAČESLAVS',
                                        'last_name': 'JEMEĻJANOVS',
                                        'middle_name': 'TV-3',
                                    },
                                },
                                'park_driver_profile_id': 'dbid1_uuid3',
                            },
                            # Driver not found
                            {
                                'data': {
                                    'car_id': 'car_id_4',
                                    'license': {'pd_id': 'pd_id_4'},
                                    'full_name': {
                                        'first_name': 'VJAČESLAVS',
                                        'last_name': 'JEMEĻJANOVS',
                                        'middle_name': 'TV-4',
                                    },
                                },
                                'park_driver_profile_id': 'dbid1_uuid4',
                            },
                            # Driver license mismatch
                            {
                                'data': {
                                    'car_id': 'car_id_5',
                                    'license': {'pd_id': 'pd_id_5'},
                                    'full_name': {
                                        'first_name': 'VJAČESLAVS',
                                        'last_name': 'WRONG_LAST_NAME',
                                        'middle_name': 'TV-5',
                                    },
                                },
                                'park_driver_profile_id': 'dbid1_uuid5',
                            },
                            # No car number in fleet-vehicles
                            {
                                'data': {
                                    'car_id': 'car_id_6',
                                    'license': {'pd_id': 'pd_id_6'},
                                    'full_name': {
                                        'first_name': 'VJAČESLAVS',
                                        'last_name': 'JEMEĻJANOVS',
                                        'middle_name': 'TV-6',
                                    },
                                },
                                'park_driver_profile_id': 'dbid1_uuid6',
                            },
                            # Driver license mismatch but ignored
                            {
                                'data': {
                                    'car_id': 'car_id_7',
                                    'license': {'pd_id': 'pd_id_6'},
                                    'full_name': {
                                        'first_name': 'VJAČESLAVS',
                                        'last_name': 'WRONG_LAST_NAME',
                                        'middle_name': 'TV-7',
                                    },
                                },
                                'park_driver_profile_id': 'dbid1_uuid7',
                            },
                            # CSDD - OK
                            {
                                'data': {
                                    'car_id': 'car_id_8',
                                    'license': {'pd_id': 'pd_id_8'},
                                    'full_name': {
                                        'first_name': 'VJAČESLAVS',
                                        'last_name': 'JEMEĻJANOVS',
                                        'middle_name': 'TV-8',
                                    },
                                },
                                'park_driver_profile_id': 'dbid1_uuid8',
                            },
                            # CSDD - Not active
                            {
                                'data': {
                                    'car_id': 'car_id_9',
                                    'license': {'pd_id': 'pd_id_9'},
                                    'full_name': {
                                        'first_name': 'VJAČESLAVS',
                                        'last_name': 'JEMEĻJANOVS',
                                        'middle_name': 'TV-9',
                                    },
                                },
                                'park_driver_profile_id': 'dbid1_uuid9',
                            },
                            # CSDD - Not found
                            {
                                'data': {
                                    'car_id': 'car_id_10',
                                    'license': {'pd_id': 'pd_id_10'},
                                    'full_name': {
                                        'first_name': 'VJAČESLAVS',
                                        'last_name': 'JEMEĻJANOVS',
                                        'middle_name': 'TV-10',
                                    },
                                },
                                'park_driver_profile_id': 'dbid1_uuid10',
                            },
                            # CSDD - Error
                            {
                                'data': {
                                    'car_id': 'car_id_11',
                                    'license': {'pd_id': 'pd_id_11'},
                                    'full_name': {
                                        'first_name': 'VJAČESLAVS',
                                        'last_name': 'JEMEĻJANOVS',
                                        'middle_name': 'TV-11',
                                    },
                                },
                                'park_driver_profile_id': 'dbid1_uuid11',
                            },
                        ],
                    },
                ],
            },
        )

    ctx.handler = mocked_dp_handler
    return ctx


@dataclasses.dataclass
class FleetVehiclesContext:
    handler: Any = None


@pytest.fixture
async def mock_fleet_vehicles_ctx(mock_fleet_vehicles):
    ctx = FleetVehiclesContext()

    @mock_fleet_vehicles('/v1/vehicles/cache-retrieve')
    async def mocked_fleet_vehicles_handler(request):
        assert request.json == {
            'id_in_set': [
                'dbid1_car_id_1',
                'dbid1_car_id_2',
                'dbid1_car_id_3',
                'dbid1_car_id_4',
                'dbid1_car_id_5',
                'dbid1_car_id_6',
                'dbid1_car_id_7',
                'dbid1_car_id_8',
                'dbid1_car_id_9',
                'dbid1_car_id_10',
                'dbid1_car_id_11',
            ],
            'projection': ['data.number'],
        }
        return web.json_response(
            {
                'vehicles': [
                    {
                        'data': {'number': 'T-1'},
                        'park_id_car_id': 'dbid1_car_id_1',
                    },
                    {
                        'data': {'number': 'T-1'},
                        'park_id_car_id': 'dbid1_car_id_2',
                    },
                    {
                        'data': {'number': 'T3_PERMIT_EXPIRED'},
                        'park_id_car_id': 'dbid1_car_id_3',
                    },
                    {
                        'data': {'number': 'T1'},
                        'park_id_car_id': 'dbid1_car_id_4',
                    },
                    {
                        'data': {'number': 't--1'},
                        'park_id_car_id': 'dbid1_car_id_5',
                    },
                    # No car number
                    {'park_id_car_id': 'dbid1_car_id_6'},
                    {
                        'data': {'number': 't--1'},
                        'park_id_car_id': 'dbid1_car_id_7',
                    },
                    {
                        'data': {'number': 'TQ1'},
                        'park_id_car_id': 'dbid1_car_id_8',
                    },
                    {
                        'data': {'number': 'TQ2'},
                        'park_id_car_id': 'dbid1_car_id_9',
                    },
                    {
                        'data': {'number': 'TQ3'},
                        'park_id_car_id': 'dbid1_car_id_10',
                    },
                    {
                        'data': {'number': 'TQ4'},
                        'park_id_car_id': 'dbid1_car_id_11',
                    },
                ],
            },
        )

    ctx.handler = mocked_fleet_vehicles_handler
    return ctx


@dataclasses.dataclass
class PersonalContext:
    handler: Any = None


@pytest.fixture
def mock_personal_ctx(mock_personal):
    ctx = PersonalContext()

    @mock_personal('/v1/driver_licenses/bulk_retrieve')
    def mocked_personal_handler(request):
        assert request.json['items'] == [
            {'id': 'pd_id_1'},
            {'id': 'pd_id_2'},
            {'id': 'pd_id_3'},
            {'id': 'pd_id_4'},
            {'id': 'pd_id_5'},
            {'id': 'pd_id_6'},
            {'id': 'pd_id_6'},
            {'id': 'pd_id_8'},
            {'id': 'pd_id_9'},
            {'id': 'pd_id_10'},
            {'id': 'pd_id_11'},
        ]

        return web.json_response(
            {
                'items': [
                    {'id': 'pd_id_1', 'value': 'LATLICENSE\t'},
                    {'id': 'pd_id_2', 'value': 'LATLICENSE'},
                    {'id': 'pd_id_3', 'value': 'LATLICENSE'},
                    {'id': 'pd_id_4', 'value': 'LATLICENSE'},
                    {'id': 'pd_id_5', 'value': 'LATLICENSE5'},
                    {'id': 'pd_id_6', 'value': 'LATLICENSE'},
                    {'id': 'pd_id_8', 'value': 'LATLICENSE'},
                    {'id': 'pd_id_9', 'value': 'LATLICENSE'},
                    {'id': 'pd_id_10', 'value': 'LATLICENSE'},
                    {'id': 'pd_id_11', 'value': 'LATLICENSE'},
                ],
            },
        )

    ctx.handler = mocked_personal_handler
    return ctx


@dataclasses.dataclass
class CsddContext:
    handler: Any = None


@pytest.fixture
def mock_csdd_ctx(mockserver):
    ctx = CsddContext()

    @mockserver.handler('csdd-api')
    def mocked_csdd(request):
        assert 'rn1' in request.query
        assert request.headers['authorization'] == 'Basic dXNlcjpwYXNz'
        if request.query['rn1'] == 'TQ1':
            return mockserver.make_response(
                """<?xml version="1.0" encoding="WINDOWS-1257" ?><YAND>
                <RN>TQ1</RN>
                <LICENCE>1</LICENCE>
                </YAND>""",
                content_type='text/html',
                charset='windows-1257',
            )
        if request.query['rn1'] == 'TQ2':
            return mockserver.make_response(
                """<?xml version="1.0" encoding="WINDOWS-1257" ?><YAND>
                <RN>TQ2</RN>
                <LICENCE>0</LICENCE>
                </YAND>""",
                content_type='text/html',
                charset='windows-1257',
            )
        if request.query['rn1'] == 'TQ3':
            return mockserver.make_response(
                """<?xml version="1.0" encoding="WINDOWS-1257" ?><YAND>
                <ERR>Nepareizs numurs</ERR>
                </YAND>""",
                content_type='text/html',
                charset='windows-1257',
            )
        if request.query['rn1'] == 'TQ4':
            return mockserver.make_response('', status=500)
        raise ValueError(request.query['rn1'])

    ctx.handler = mocked_csdd
    return ctx


@dataclasses.dataclass
class TagsContext:
    blocked_drivers: list
    blocked_cars: list
    unblocked_drivers: list
    unblocked_cars: list
    handler: Any = None


@pytest.fixture
def mock_tags_ctx(mock_tags):
    ctx = TagsContext([], [], [], [])

    @mock_tags('/v2/upload')
    async def mocked_tags_handler(request):
        for append in request.json.get('append', []):
            if append['entity_type'] == 'dbid_uuid':
                ctx.blocked_drivers.extend(
                    (tag['entity'] for tag in append['tags']),
                )
            else:
                ctx.blocked_cars.extend(
                    (tag['entity'] for tag in append['tags']),
                )
        for remove in request.json.get('remove', []):
            if remove['entity_type'] == 'dbid_uuid':
                ctx.unblocked_drivers.extend(
                    (tag['entity'] for tag in remove['tags']),
                )
            else:
                ctx.unblocked_cars.extend(
                    (tag['entity'] for tag in remove['tags']),
                )
        return web.json_response({'status': 'ok'})

    ctx.handler = mocked_tags_handler
    return ctx


@pytest.fixture
def proxy_in_secdist(simple_secdist):
    simple_secdist['EUROPE_PROXY'] = {
        'username': 'proxy_username',
        'password': 'proxy_password',
    }
    simple_secdist['ATD'] = {
        'username': 'atd_username',
        'password': 'atd_password',
    }
    simple_secdist['CSDD'] = {'username': 'user', 'password': 'pass'}


@pytest.fixture(autouse=True)
def mock_solomon(mockserver):
    @mockserver.handler('/solomon/')
    def _mock_solomon(request):
        return mockserver.make_response('')
