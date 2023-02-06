"""
    Describe here service specific fixtures.
"""
# pylint: disable=redefined-outer-name
import base64
import copy
import datetime
import json
import typing
import uuid

import pytest


class CargoDispatchWaybills:
    """
    Cargo-dispatch waybills and journal context.
    """

    entries: typing.List[typing.Dict]
    waybills: typing.Dict[str, typing.Dict]
    propositions: typing.Dict[str, typing.Dict]
    known_waybills: typing.Set[str]
    last_cursor: typing.Optional[str]

    def __init__(self) -> None:
        self.entries = []
        self.waybills = {}
        self.propositions = {}
        self.known_waybills = set()
        self.last_cursor = None

    def add_journal_entry(self, waybill: dict):
        entry = {
            'created_ts': '2021-09-23T16:12:50.541292+00:00',
            'revision': waybill['dispatch']['revision'],
            'external_ref': waybill['waybill']['external_ref'],
            'current': {},
        }
        self.entries.append(entry)

    def update_waybill(self, waybill: dict):
        waybill_id = waybill['waybill']['external_ref']

        if not self.has_waybill(waybill_id):
            raise RuntimeError(f'Waybill {waybill_id} does not exists')

        self.waybills[waybill_id] = waybill
        self.add_journal_entry(waybill)

    def add_waybill(self, waybill: dict):
        waybill_id = waybill['waybill']['external_ref']

        # check unique constraint: waybill_id
        if waybill_id in self.known_waybills:
            raise RuntimeError(f'Waybill {waybill_id} already exists')
        self.known_waybills.add(waybill_id)

        self.waybills[waybill_id] = waybill
        self.add_journal_entry(waybill)

    def get_waybill(self, waybill_ref: str):
        if self.has_waybill(waybill_ref):
            return self.waybills.get(waybill_ref)
        return None

    def has_waybill(self, waybill_ref: str):
        return waybill_ref is not None and waybill_ref in self.waybills

    def read_journal(self, cursor: typing.Optional[str] = None):
        index = _deserialize_cursor(cursor)
        items = self.entries[index:]
        cursor = _serialize_cursor(len(self.entries))
        self.last_cursor = cursor
        return items, cursor


class CargoDispatchSegments:
    """
    Cargo-dispatch segments and journal context.
    """

    entries: typing.List[typing.Dict]
    segments: typing.Dict[str, typing.Dict]
    known_segments: typing.Set[str]
    known_points: typing.Set[str]
    last_cursor: typing.Optional[str]

    def __init__(self) -> None:
        self.entries = []
        self.segments = {}
        self.known_segments = set()
        self.known_points = set()
        self.last_cursor = None

    def add_journal_entry(self, doc: dict):
        entry = {
            'created_ts': '2021-09-23T16:07:50.541292+00:00',
            'revision': doc['dispatch']['revision'],
            'segment_id': doc['segment']['id'],
            'waybill_building_version': doc['dispatch']['waybill_building_version'],
        }
        self.entries.append(entry)

    def read_journal(self, cursor: typing.Optional[str] = None):
        index = _deserialize_cursor(cursor)
        items = self.entries[index:]
        cursor = _serialize_cursor(len(self.entries))
        self.last_cursor = cursor
        return items, cursor

    def add_segment(self, doc: dict):
        segment_id = doc['segment']['id']

        # check unique constraint: segment_id
        if segment_id in self.known_segments:
            raise RuntimeError(f'Segment {segment_id} already exists')
        self.known_segments.add(segment_id)

        # check unique constraint: point_id
        points = doc['segment']['points']
        for point in points:
            point_id = point['point_id']
            if point_id in self.known_points:
                raise RuntimeError(f'Point {point_id} already exists')
        for point in points:
            self.known_points.add(point['point_id'])

        self.segments[segment_id] = doc
        self.add_journal_entry(doc)

    def get_segment(self, segment_id: str):
        if self.has_segment(segment_id):
            return self.segments.get(segment_id)
        return None

    def has_segment(self, segment_id: str):
        return segment_id is not None and segment_id in self.segments

    def inc_waybill_building_version(self, segment_id):
        doc = self.segments[segment_id]
        doc['dispatch']['waybill_building_version'] += 1
        self.add_journal_entry(doc)


class CargoDispatch:
    """
        Cargo-dispatch context.
         - segments state (info, journal)
         - waybills state (info, journal)
    """

    segments: CargoDispatchSegments
    waybills: CargoDispatchWaybills

    def __init__(self):
        self.segments = CargoDispatchSegments()
        self.waybills = CargoDispatchWaybills()

    # segment utils
    def add_segment(self, segment: dict):
        self.segments.add_segment(segment)

    def get_segment(self, segment_id: str):
        return self.segments.get_segment(segment_id)

    def has_segment(self, segment_id: str):
        return self.segments.has_segment(segment_id)

    def read_segments_journal(self, cursor: typing.Optional[str] = None):
        return self.segments.read_journal(cursor)

    # waybill utils
    def add_waybill(self, waybill: dict):
        self.waybills.add_waybill(waybill)

    def get_waybill(self, waybill_ref: str):
        return self.waybills.get_waybill(waybill_ref)

    def has_waybill(self, waybill_ref: str):
        return self.waybills.has_waybill(waybill_ref)

    def read_waybills_journal(self, cursor: typing.Optional[str] = None):
        return self.waybills.read_journal(cursor)

    def update_waybill(self, waybill: dict):
        self.waybills.update_waybill(waybill)


class PropositionsManager:
    def __init__(self):
        self.propositions = []

    def add_propositon(self, doc):
        self.propositions.append(doc)


class CandidatesContext:
    DEFAULT_SHIFT = {'shift_id': '0', 'status': 'in_progress'}

    def __init__(self):
        self._candidates = {}

    def add_candidate(
        self,
        *,
        tariff_classes: typing.List[str],
        position: typing.Tuple[float, float],
        transport_type: str = 'car',
        dbid_uuid: typing.Optional[str] = None,
        eats_shift: typing.Optional[dict] = None,
        grocery_shift: typing.Optional[dict] = None,
        chain_info: typing.Optional[dict] = None,
    ):
        if dbid_uuid is None:
            candidate_dbid = uuid.uuid4().hex
            candidate_uuid = uuid.uuid4().hex
            dbid_uuid = candidate_dbid + '_' + candidate_uuid
        else:
            candidate_dbid, candidate_uuid = dbid_uuid.split('_')

        self._candidates[dbid_uuid] = {
            'id': dbid_uuid,
            'dbid': candidate_dbid,
            'uuid': candidate_uuid,
            'tariff_classes': tariff_classes,
            'classes': tariff_classes,
            'position': position,
            'transport': {'type': transport_type},
            'eats_shift': eats_shift
            or copy.deepcopy(
                CandidatesContext.DEFAULT_SHIFT,
            ),
            'grocery_shift': grocery_shift
            or copy.deepcopy(
                CandidatesContext.DEFAULT_SHIFT,
            ),
        }
        if chain_info is not None:
            self._candidates[dbid_uuid]['chain_info'] = chain_info

        return dbid_uuid

    @property
    def candidates(self):
        return self._candidates


@pytest.fixture
def cargo_dispatch():
    return CargoDispatch()


@pytest.fixture
def propositions_manager(run_watchers):
    return PropositionsManager()


@pytest.fixture
def candidates_context():
    return CandidatesContext()


@pytest.fixture
def create_candidate(candidates_context, mock_candidates):
    return candidates_context.add_candidate


@pytest.fixture(name='upsert_robot_state')
async def _upsert_robot_state(pgsql):
    def wrapper(name, state, *, status=None):
        if status is None:
            status = '{"status":"ACTIVE","last_flush":1632400798,' '"host":"rva3ukeypv63m5rm.sas.yp-c.yandex.net"}'
        cursor = pgsql['logistic_dispatcher'].cursor()
        cursor.execute(
            """
            INSERT INTO rt_background_state
                (
                    bp_name,
                    bp_type,
                    bp_state,
                    bp_status
                )
            VALUES (
                %(name)s,
                'some_robot',
                %(state)s,
                %(status)s
            )
            ON CONFLICT (bp_name) DO UPDATE SET
                bp_state = EXCLUDED.bp_state,
                bp_status = EXCLUDED.bp_status
            """,
            dict(name=name, state=state, status=status),
        )

    return wrapper


@pytest.fixture(name='upsert_robot_settings')
async def _upsert_robot_settings(pgsql):
    def wrapper(name, settings, *, enabled=True):
        cursor = pgsql['logistic_dispatcher'].cursor()
        cursor.execute(
            """
            INSERT INTO rt_background_settings
                (
                    bp_name,
                    bp_type,
                    bp_settings,
                    bp_enabled
                )
            VALUES (
                %(name)s,
                'some_robot',
                %(settings)s,
                %(enabled)s
            )
            ON CONFLICT (bp_name) DO UPDATE SET
                bp_settings = EXCLUDED.bp_settings,
                bp_enabled = EXCLUDED.bp_enabled
            """,
            dict(name=name, settings=settings, enabled=enabled),
        )

    return wrapper


@pytest.fixture(name='get_worker_state')
async def _get_worker_state(pgsql):
    def wrapper(worker_name):
        cursor = pgsql['united_dispatch'].dict_cursor()
        cursor.execute(
            """
            SELECT
                payload
            FROM united_dispatch.worker_state
            WHERE worker_name = %s
            """,
            (worker_name,),
        )
        state = cursor.fetchone()
        if state is None:
            return None
        return state['payload']

    return wrapper


@pytest.fixture(name='waybill_builder')
async def _waybill_builder(load_json_var):
    def wrapper(
            *,
            waybill_ref,
            segment_id=None,
            resolution='',
            status='processing',
            template='cargo-dispatch/waybill.json',
            **kwargs,
    ):
        response = load_json_var(
            template,
            waybill_ref=waybill_ref,
            resolution=resolution,
            status=status,
            segment_id=segment_id,
            pickup_point=f'{segment_id}/pickup',
            dropoff_point=f'{segment_id}/dropoff',
            return_point=f'{segment_id}/return',
            **kwargs,
        )

        return response

    return wrapper


@pytest.fixture(name='segment_builder')
async def _segment_builder(load_json_var):
    def wrapper(
        *,
        segment_id,
        waybill_building_awaited=True,
        max_route_distance_courier=11520,
        waybill_building_version=1,
        modified_classes=None,
        tariffs_substitution=None,
        additional_taxi_requirements=None,
        segment_custom_context=None,
        corp_client_id='70a499f9eec844e9a758f4bc33e667c0',
        employer='default',
        item_weight=None,
        template='cargo-dispatch/segment.json',
        crutches=None,
        **kwargs,
    ):
        if 'waybill_building_deadline' not in kwargs:
            deadline = datetime.datetime.utcnow() - datetime.timedelta(
                minutes=5,
            )
            kwargs['waybill_building_deadline'] = f'{deadline.isoformat()}+00:00'
        response = load_json_var(
            template,
            segment_id=segment_id,
            waybill_building_awaited=waybill_building_awaited,
            waybill_building_version=waybill_building_version,
            max_route_distance_courier=max_route_distance_courier,
            pickup_point=f'{segment_id}/pickup',
            dropoff_point=f'{segment_id}/dropoff',
            return_point=f'{segment_id}/return',
            mandatory_return_point=f'{segment_id}/mandatory_return',
            corp_client_id=corp_client_id,
            client_payment_method=f'corp-{corp_client_id}',
            **kwargs,
        )
        if modified_classes is not None:
            response['dispatch']['modified_classes'] = modified_classes
        if tariffs_substitution is not None:
            response['dispatch']['tariffs_substitution'] = tariffs_substitution
        if additional_taxi_requirements:
            response['segment']['performer_requirements'].update(
                additional_taxi_requirements,
            )
        if segment_custom_context is not None:
            response['segment']['custom_context'] = segment_custom_context

        response['segment']['employer'] = employer
        if item_weight is not None:
            response['segment']['items'][0]['weight'] = item_weight

        if crutches is not None:
            response['segment']['claim_comment'] = _build_crutch_comment(
                response['segment'].get('claim_comment'),
                crutches,
            )

        return response

    return wrapper


@pytest.fixture
def create_waybill(waybill_builder, cargo_dispatch: CargoDispatch):
    def waybill_creator(
            *,
            waybill_ref=None,
            segment_id=None,
            resolution=None,
            status=None,
            **kwargs,
    ):
        if waybill_ref is None:
            waybill_ref = uuid.uuid4().hex

        new_waybill = waybill_builder(
            waybill_ref=waybill_ref,
            resolution=resolution,
            status=status,
            segment_id=segment_id,
            **kwargs,
        )
        cargo_dispatch.add_waybill(new_waybill)
        return waybill_ref

    return waybill_creator


@pytest.fixture
def read_waybill(cargo_dispatch: CargoDispatch):
    def wrapper(*, waybill_ref, **kwargs):
        return cargo_dispatch.get_waybill(waybill_ref=waybill_ref)

    return wrapper


@pytest.fixture
def update_waybill(cargo_dispatch: CargoDispatch):
    def wrapper(*, waybill, **kwargs):
        cargo_dispatch.update_waybill(waybill)

    return wrapper


@pytest.fixture
def create_segment(
    mock_segment_dispatch_journal,
    mock_dispatch_segment,
    segment_builder,
    cargo_dispatch: CargoDispatch,
):
    def segment_creator(*, segment_id=None, zone_id=None, dropoff_point_location=None, custom_context=None, **kwargs):
        if segment_id is None:
            segment_id = uuid.uuid4().hex
        if zone_id is None:
            zone_id = 'moscow'
        if dropoff_point_location is None:
            dropoff_point_location=uuid.uuid4().hex

        doc = segment_builder(
            segment_id=segment_id,
            zone_id=zone_id,
            dropoff_point_location=dropoff_point_location,
            segment_custom_context=custom_context,
            **kwargs,
        )
        cargo_dispatch.add_segment(doc)
        return doc['segment']['id']

    return segment_creator


@pytest.fixture(name='execute_pg_query')
async def _execute_pg_query(pgsql):
    def wrapper(query, db='ld'):
        cursor = pgsql[db].dict_cursor()
        cursor.execute(query)
        return cursor.fetchall()

    return wrapper


@pytest.fixture(name='print_pg_table')
async def _print_pg_table(pgsql):
    def wrapper(table_name, db='ld', schema=None):
        print(f'\n\n\n{schema}.{table_name} ROWS:')
        cursor = pgsql[db].dict_cursor()
        if schema is None:
            cursor.execute(f'select * from {table_name}')
        else:
            cursor.execute(f'select * from {schema}.{table_name}')
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            print(f'\t{dict(row)}')

    return wrapper


@pytest.fixture(name='print_pg_database')
async def _print_pg_database(print_pg_table, pgsql):
    def wrapper(db='ld'):
        cursor = pgsql[db].dict_cursor()
        cursor.execute('select table_name from information_schema.tables where table_schema=\'public\'')
        while True:
            row = cursor.fetchone()
            if row is None:
                break

            table_name = dict(row)['table_name']
            print_pg_table(table_name, db)

    return wrapper


@pytest.fixture(name='get_segment')
async def _get_segment(pgsql):
    def wrapper(segment_id):
        cursor = pgsql['united_dispatch'].dict_cursor()
        cursor.execute(
            """
                SELECT
                    id,
                    waybill_building_version,
                    is_waybill_send,
                    dispatch_revision,
                    taxi_classes,
                    taxi_requirements,
                    special_requirements,
                    points
                FROM united_dispatch.segments WHERE id = %(segment_id)s
            """,
            dict(segment_id=segment_id),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    return wrapper


def _build_crutch_comment(comment, crutches):
    crutch_str = f'$$${json.dumps(crutches)}$$$'
    if not comment:
        return crutch_str
    return f'{comment} {crutch_str}'


def _serialize_cursor(index: int) -> str:
    return base64.b64encode(
        json.dumps({'index': index}).encode('utf-8'),
    ).decode()


def _deserialize_cursor(cursor: typing.Optional[str]) -> int:
    if not cursor:
        return 0
    doc = json.loads(base64.b64decode(cursor))
    return doc['index']


@pytest.fixture(name="default_configs_v3", autouse=True)
def _default_configs_v3(mockserver):
    @mockserver.json_handler('/v1/configs')
    def experiments(request):
        return {
            'items': [],
            'version': 0,
        }


@pytest.fixture(name="cargo_eta_flow_config")
def _cargo_eta_flow_config(mockserver):
    @mockserver.json_handler('/v1/configs')
    def experiments(request):
        # see https://wiki.yandex-team.ru/taxi/backend/architecture/experiments3/http/#primeryispolzovanija
        r = request.json
        if r['consumer'] != 'logistic-dispatcher/simple_p2p_tactic_apply':
            return {'items': [], 'version': 0}

        return {
            'items': [
                {'name': 'cargo_eta_flow', 'value': {
                    'calc_eta_from': [
                        'logistic-dispatcher'
                    ],
                    'return_eta_from': 'logistic-dispatcher'
                }},
            ],
            'version': 0,
        }


@pytest.fixture
def dummy_candidates(mockserver):
    def wrapper(*, chain_info=None, shift=None, max_weight=None, transport='car', position=[37.51, 55.76]):
        @mockserver.json_handler('/candidates/order-search')
        def order_search(request):
            response = {
                'candidates': [
                    {
                        'car_id': 'd08b0e4d8360010cb27f19659ea3f96e',
                        'car_number': 'Н792ВР76',
                        'classes': ['courier', 'lavka'],
                        'dbid': '61d2e5ef6aaa4fe88dcc916eb5838473',
                        'id': '61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8',
                        'license_id': '1677495cbb1a41b38ab3d71813c2569e',
                        'metadata': {},
                        'position': position,
                        'position_info': {
                            'timestamp': '2021-11-29T16:58:12+00:00',
                        },
                        'route_info': {
                            'approximate': False,
                            'distance': 10,
                            'properties': {'toll_roads': False},
                            'time': 20,
                        },
                        'status': {
                            'driver': 'free',
                            'orders': [],
                            'status': 'online',
                            'taximeter': 'free',
                        },
                        'transport': {'type': transport},
                        'unique_driver_id': '5a201c5751baddbf5b24469b',
                        'uuid': '71bb0041d4214b0e9a7eb35614917da8',
                    },
                ],
            }
            if chain_info is not None:
                for candidate in response['candidates']:
                    candidate['chain_info'] = chain_info
            if max_weight is not None:
                for candidate in response['candidates']:
                    candidate['logistic'] = {'weight': {'max': max_weight * 1000}}
            return response

        @mockserver.json_handler('/candidates/profiles')
        def profiles(request):
            response = {
                'drivers': [
                    {
                        'id': '61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8',
                        'uuid': '71bb0041d4214b0e9a7eb35614917da8',
                        'dbid': '61d2e5ef6aaa4fe88dcc916eb5838473',
                        'position': position,
                        'classes': ['courier', 'lavka'],
                    },
                ],
            }
            if shift is not None:
                response['drivers'][0]['eats_shift'] = shift

            return response

    return wrapper


@pytest.fixture
def dummy_geoareas(mockserver):
    async def wrapper(*, employer_names=None, order_sources=None, polygon=None):
        @mockserver.json_handler('/internal/v1/caches/slot-dispatch-settings/updates')
        def slot_dispatch_settings(request):
            response = {
                'slot_dispatch_settings': [
                    {
                        'data': {
                            'version': 2
                        },
                        'slot_id': 'c6da02e2-4d1b-490d-8246-723e15323a82'
                    }
                ],
                'cache_lag': 1,
                'last_revision': '2022-03-20T14:00:41+0000_718143',
                'last_modified': '2022-03-20T14:00:41Z'
            }
            if employer_names is not None:
                response['slot_dispatch_settings'][0]['data']['employer_names'] = employer_names
            if order_sources is not None:
                response['slot_dispatch_settings'][0]['data']['order_sources'] = order_sources
            if polygon is not None:
                response['slot_dispatch_settings'][0]['data']['polygon'] = polygon
            return response

        @mockserver.json_handler('/internal/v1/caches/slot-subscribers/updates')
        def slot_subscribers(request):
            return {
                'slot_subscribers': [
                    {
                        'data': {
                            'slot_id': 'c6da02e2-4d1b-490d-8246-723e15323a82',
                            'version': 2
                        },
                        'contractor_id': '61d2e5ef6aaa4fe88dcc916eb5838473_71bb0041d4214b0e9a7eb35614917da8'
                    }
                ],
                'cache_lag': 1,
                'last_revision': '2022-03-20T14:00:41+0000_718143',
                'last_modified': '2022-03-20T14:00:41Z'
            }
    return wrapper
