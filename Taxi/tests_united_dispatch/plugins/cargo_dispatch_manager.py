"""
    Describe here cargo-dispatch service specific fixtures.
"""
# pylint: disable=redefined-outer-name
import base64
import copy
import dataclasses
import datetime
import json
import typing
import uuid


@dataclasses.dataclass
class Point:
    segment_id: str
    point_type: str  # pickup | dropoff | return
    coordinates: typing.List[float]
    external_order_id: typing.Optional[str] = None
    due: typing.Optional[str] = None
    point_id: str = dataclasses.field(
        default_factory=lambda: str(uuid.uuid4()),
    )
    location_id: str = dataclasses.field(
        default_factory=lambda: str(uuid.uuid4()),
    )  # id of this location, differs from point id
    is_visited: bool = False  # resolution = visited
    is_skipped: bool = False  # resolution = skipped
    time_intervals: typing.Optional[typing.List] = None

    @property
    def is_resolved(self):
        return self.is_visited or self.is_skipped

    @property
    def resolution(self):
        if self.is_resolved:
            return {
                'is_visited': self.is_visited,
                'is_skipped': self.is_skipped,
            }
        return None

    @property
    def visit_status(self):
        if self.is_visited:
            return 'visited'
        if self.is_skipped:
            return 'skipped'
        return 'pending'

    def __post_init__(self):
        assert not (
            self.is_visited and self.is_skipped
        ), 'Only one resolution possible'
        assert self.point_type in {'pickup', 'dropoff', 'return'}


@dataclasses.dataclass
class ItemSizes:
    length: float
    width: float
    height: float


@dataclasses.dataclass
class SegmentItem:
    item_id: str
    quantity: int
    # Not used in UD; required for cargo schema validation
    # {
    pickup_point: str = 'cfddc348-e716-464f-bd4e-fae98f11157d'
    dropoff_point: str = 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce'
    return_point: str = '4d7a74ff-9299-4091-9b9a-fc05b780091b'
    title: str = 'test_title'
    # }

    size: typing.Optional[ItemSizes] = None
    weight: typing.Optional[float] = None


@dataclasses.dataclass
class Segment:
    points: typing.List[Point]  # sorted by visit_order

    taxi_classes: typing.List[str]
    taxi_requirements: typing.Dict[str, typing.Any]
    # taxi_class -> spec_req_ids
    special_requirements: typing.Dict[str, typing.Set[str]]
    custom_context: typing.Dict[str, typing.Any]
    crutches: typing.Dict[str, typing.Any]

    id: str = dataclasses.field(  # pylint: disable=invalid-name
        default_factory=lambda: str(uuid.uuid4()),
    )
    waybill_building_version: int = 1  # gamble version
    revision: int = 1
    resolution: typing.Optional[str] = None  # resolved/cancelled_by_user/...

    corp_client_id: typing.Optional[str] = dataclasses.field(
        default_factory=lambda: uuid.uuid4().hex,
    )  # corporative client who made an order
    zone_id: str = 'moscow'
    waybill_building_awaited: bool = True  # started waiting for waybill
    waybill_building_deadline: str = '2021-09-23T15:38:47.185337+00:00'
    allow_alive_batch_v1: bool = True
    allow_alive_batch_v2: bool = True
    allow_batch: bool = True
    status: str = 'performer_found'  # external segment status
    modified_classes: typing.Optional[typing.List[str]] = None
    tariffs_substitution: typing.Optional[typing.List[str]] = None
    comment: str = ''
    chosen_waybill: typing.Optional[typing.Dict] = None
    estimations: typing.Optional[typing.Any] = None
    planner: typing.Optional[str] = None
    routers: typing.Optional[typing.Tuple[typing.Dict]] = (
        {
            'id': 'united-dispatch',
            'source': 'cargo-dispatch-choose-routers',
            'matched_experiment': {
                'name': 'segment_routers',
                'clause_index': '20',
            },
            'priority': 1,
            'autoreorder_flow': 'newway',
        },
    )

    items: typing.List[
        SegmentItem
    ] = dataclasses.field(  # pylint: disable=invalid-name
        default_factory=lambda: [
            SegmentItem(
                item_id='bf0d5230ab544d29b5dc0a785aaa169c',
                size=ItemSizes(length=0, width=0, height=0),
                weight=0,
                quantity=1,
            ),
        ],
    )
    created_ts: datetime.datetime = datetime.datetime(
        year=2020, month=1, day=22,
    )

    claim_features: typing.List[
        dict
    ] = dataclasses.field(  # pylint: disable=invalid-name
        default_factory=lambda: [],
    )

    claim_origin: typing.Optional[str] = None

    def __post_init__(self):
        # fill planner to decide which planner to run
        if self.planner:
            return
        if self.crutches:
            self.planner = 'crutches'
        elif self.corp_client_id in {
            'eats_corp_id',
            'eats_corp_id1',
            'eats_corp_id2',
            'food_retail_corp_id1',
        }:
            self.planner = 'eats'
        elif self.corp_client_id in {'grocery_corp_id1'}:
            self.planner = 'grocery'
        elif self.corp_client_id == 'candidates-testsuite':
            self.planner = 'testsuite-candidates'
        else:
            self.planner = 'delivery'

    def build_comment(self):
        if not self.crutches:
            return self.comment
        crutch_str = f'$$${json.dumps(self.crutches)}$$$'
        if not self.comment:
            return crutch_str
        return f'{self.comment} {crutch_str}'

    def add_point(self, point: Point):
        self.points.append(point)

    def set_resolution(self, status: str, resolution: str):
        self.status = status
        self.resolution = resolution

    @property
    def chosen_waybill_ref(self):
        if not self.chosen_waybill:
            return None
        # pylint: disable=unsubscriptable-object
        return self.chosen_waybill['external_ref']


@dataclasses.dataclass
class WaybillUpdateProposition:
    previous_waybill_ref: str
    previous_waybill_revision: int


# initalize on /propose
@dataclasses.dataclass
class Waybill:
    # aka external_ref/waybill_ref
    id: str  # pylint: disable=invalid-name
    taxi_classes: typing.List[str]
    taxi_requirements: typing.Dict[str, typing.Any]  # merged from segments
    special_requirements: typing.Dict[str, typing.Any]  # merged from segments

    segments: typing.List[Segment]
    points: typing.List[Point]  # sorted by visit_order

    revision: int = 1  # external modification increment
    status: str = 'processing'  # external waybill status, not stored
    resolution: typing.Optional[str] = None  # external resolution, not stored

    is_accepted: bool = False  # not stored in UD, live batch accepted
    is_declined: bool = False  # not stored in UD, waybill removed if True

    performer_id: typing.Optional[str] = None  # dbid_uuid
    # uses for race resolving
    performer_found_ts: str = '2021-12-14T10:00:00.000000+00:00'
    performer_tariff: typing.Optional[str] = None

    taxi_order_id: typing.Optional[str] = None
    cargo_order_id: typing.Optional[str] = None  # not stored

    update_proposition: typing.Optional[WaybillUpdateProposition] = None

    def __post_init__(self):
        # check segments and points
        pass

    def get_current_point(
            self,
    ) -> typing.Tuple[typing.Optional[int], typing.Optional[Point]]:
        for idx, point in enumerate(self.points):
            if not point.is_resolved:
                if (
                        point.point_type == 'return'
                        and not self.is_return_required()
                ):
                    return None, None
                return idx, point
        return None, None

    def get_last_point(self) -> typing.Tuple[int, Point]:
        return len(self.points) - 1, self.points[-1]

    def get_point(self, *, visit_order: int):
        for idx, point in enumerate(self.points):
            if idx == visit_order:
                return point
        return None

    def set_performer(
            self, performer_id: str = None, performer_tariff: str = None,
    ):
        if performer_id is None:
            performer_id = uuid.uuid4().hex + '_' + uuid.uuid4().hex

        if performer_tariff is None:
            performer_tariff = 'express'

        self.performer_id = performer_id
        self.performer_tariff = performer_tariff

    def set_point_resolution(
            self, visit_order: int, is_visited=True, is_skipped=False,
    ):
        if is_visited and is_skipped:
            raise RuntimeError('both resolutions for point is not allowed')
        if not is_visited and not is_skipped:
            raise RuntimeError('pass at least one resolution for point')

        self.revision += 1

        point = self.get_point(visit_order=visit_order)
        if not point:
            raise RuntimeError(f'point not found by visit order {visit_order}')

        point.is_visited = is_visited
        point.is_skipped = is_skipped
        return point

    def is_return_required(self):
        for point in self.points:
            if point.is_skipped and point.point_type == 'pickup':
                return True
        return False


class CargoDispatchSegments:
    """
    Cargo-dispatch segments and journal context.
    """

    journal_entries: typing.List[typing.Dict]
    segments: typing.Dict[str, Segment]
    known_docs: typing.Set[str]
    known_points: typing.Set[str]
    last_cursor: typing.Optional[str]

    def __init__(self) -> None:
        self.journal_entries = []
        self.segments = {}
        self.known_docs = set()
        self.known_points = set()
        self.last_cursor = None

    def get_segment(self, segment_id: str):
        return self.segments.get(segment_id)

    def add_journal_entry(self, segment: Segment):
        entry = {
            'created_ts': '2021-09-23T16:07:50.541292+00:00',
            'revision': segment.revision,
            'segment_id': segment.id,
            'waybill_building_version': segment.waybill_building_version,
        }
        self.journal_entries.append(entry)

    def read_journal(self, cursor: typing.Optional[str] = None):
        index = _deserialize_cursor(cursor)
        items = self.journal_entries[index:]
        cursor = _serialize_cursor(len(self.journal_entries))
        self.last_cursor = cursor
        return items, cursor

    def add_segment(self, segment: Segment):
        # check unique constraint: segment_id
        if segment.id in self.known_docs:
            raise RuntimeError(f'Segment {segment.id} already exists')
        self.known_docs.add(segment.id)

        # check unique constraint: point_id
        for point in segment.points:
            point_id = point.point_id
            if point_id in self.known_points:
                raise RuntimeError(f'Point {point_id} already exists')
        for point in segment.points:
            self.known_points.add(point.point_id)

        self.segments[segment.id] = segment
        self.add_journal_entry(segment)

    def inc_waybill_building_version(self, segment_id):
        segment = self.segments[segment_id]
        assert segment is not None, f'Segment {segment_id} not found'
        segment.waybill_building_version += 1
        self.add_journal_entry(segment)

    def inc_revision(self, segment_id):
        segment = self.segments[segment_id]
        assert segment is not None, f'Segment {segment_id} not found'
        segment.revision += 1
        self.add_journal_entry(segment)

    def set_resolution(self, segment_id, resolution='cancelled_by_user'):
        segment = self.segments[segment_id]
        assert segment is not None, f'Segment {segment_id} not found'
        segment.resolution = resolution
        self.add_journal_entry(segment)

    def set_routers(self, segment_id, routers):
        segment = self.segments[segment_id]
        assert segment is not None, f'Segment {segment_id} not found'
        segment.routers = routers
        segment.revision += 1
        self.add_journal_entry(segment)

    def set_proposition(self, segment_id, external_ref):
        segment = self.segments[segment_id]
        assert segment is not None, f'Segment {segment_id} not found'
        segment.chosen_waybill = _make_chosen_waybill(external_ref)
        segment.revision += 1
        self.add_journal_entry(segment)


class CargoDispatchWaybills:
    """
    Cargo-dispatch waybills and journal context.
    """

    journal_entries: typing.List[typing.Dict]  # history for journal
    waybills: typing.Dict[str, Waybill]
    propositions: typing.Dict[str, typing.Dict]  # waybill propositions
    known_docs: typing.Set[
        str
    ]  # known waybill_refs to check testsuite constraints
    last_cursor: typing.Optional[str]  # current cursor

    def __init__(self) -> None:
        self.journal_entries = []
        self.waybills = {}
        self.propositions = {}
        self.known_docs = set()
        self.last_cursor = None

    def get_waybill(self, waybill_ref: str = None, taxi_order_id: str = None):
        if waybill_ref:
            return self.waybills.get(waybill_ref)
        if taxi_order_id:
            for waybill in self.waybills.values():
                if waybill.taxi_order_id == taxi_order_id:
                    return waybill
            return None
        assert False, 'nor waybill_ref nor taxi_order_id passed'
        return None

    def get_single_waybill(self):
        assert len(self.waybills) == 1
        return next(iter(self.waybills.values()))

    def add_journal_entry(self, waybill: Waybill):
        entry = {
            'created_ts': '2021-09-23T16:12:50.541292+00:00',
            'revision': waybill.revision,
            'external_ref': waybill.id,
            'current': {},  # taxi_order_id not used in tests
        }
        self.journal_entries.append(entry)

    def read_journal(self, cursor: typing.Optional[str] = None):
        index = _deserialize_cursor(cursor)
        items = self.journal_entries[index:]
        cursor = _serialize_cursor(len(self.journal_entries))
        self.last_cursor = cursor
        return items, cursor

    def add_waybill(self, waybill: Waybill):
        # check unique constraint: segment_id
        if waybill.id in self.known_docs:
            raise RuntimeError(f'Waybill {waybill.id} already exists')
        self.known_docs.add(waybill.id)

        self.waybills[waybill.id] = waybill
        self.add_journal_entry(waybill)

    def set_taxi_order(self, waybill_ref: str):
        waybill = self.waybills[waybill_ref]
        assert waybill, f'waybill {waybill_ref} not found'

        waybill.revision += 1
        waybill.taxi_order_id = str(uuid.uuid4())
        waybill.cargo_order_id = str(uuid.uuid4())

        self.add_journal_entry(waybill)

    def set_performer(self, waybill_ref: str, **kwargs):
        waybill = self.waybills[waybill_ref]
        assert waybill, f'waybill {waybill_ref} not found'

        waybill.revision += 1
        waybill.set_performer(**kwargs)

        self.add_journal_entry(waybill)

    def drop_performer(self, waybill_ref: str):
        waybill = self.waybills[waybill_ref]
        assert waybill, f'waybill {waybill_ref} not found'

        waybill.revision += 1
        waybill.performer_id = None

        self.add_journal_entry(waybill)

    def set_resolved(self, waybill_ref: str, resolution: str = 'complete'):
        waybill = self.waybills[waybill_ref]
        assert waybill, f'waybill {waybill_ref} not found'

        waybill.revision += 1
        waybill.resolution = resolution

        self.add_journal_entry(waybill)

    def set_update_proposition_accepted(self, waybill_ref: str):
        waybill = self.waybills[waybill_ref]
        assert waybill, f'waybill {waybill_ref} not found'

        waybill.revision += 1
        waybill.status = 'processing'
        waybill.is_accepted = True

        self.add_journal_entry(waybill)

    def set_update_proposition_declined(self, waybill_ref: str):
        waybill = self.waybills[waybill_ref]
        assert waybill, f'waybill {waybill_ref} not found'

        waybill.revision += 1
        waybill.resolution = 'declined'
        waybill.is_declined = True

        self.add_journal_entry(waybill)

    def drop_update_proposition(self, waybill_ref: str):
        waybill = self.waybills[waybill_ref]
        assert waybill, f'waybill {waybill_ref} not found'

        # sometimes happens in cargo-dispatch
        self.waybills.pop(waybill_ref)

        waybill.revision += 1
        self.add_journal_entry(waybill)

    def set_point_resolution(
            self,
            waybill_ref: str,
            visit_order: int,
            is_visited=True,
            is_skipped=False,
    ):
        waybill = self.waybills[waybill_ref]
        assert waybill, f'waybill {waybill_ref} not found'

        waybill.set_point_resolution(
            visit_order=visit_order,
            is_visited=is_visited,
            is_skipped=is_skipped,
        )

        self.add_journal_entry(waybill)


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
    def add_segment(self, segment: Segment):
        self.segments.add_segment(segment)

    def get_segment(self, segment_id: str):
        return self.segments.get_segment(segment_id)

    # waybill utils
    def add_waybill(self, waybill: Waybill):
        self.waybills.add_waybill(waybill)

    def get_waybill(self, **kwargs):
        return self.waybills.get_waybill(**kwargs)

    def get_single_waybill(self):
        return self.waybills.get_single_waybill()


class PropositionsManager:
    def __init__(self):
        self.propositions = []
        self.live_propositions = {}

    def add_propositon(self, doc):
        self.propositions.append(doc)

    def add_live_proposition(self, previous_waybill_ref, doc):
        self.live_propositions[previous_waybill_ref] = doc


def _serialize_cursor(index: int) -> str:
    return base64.b64encode(
        json.dumps({'index': index}).encode('utf-8'),
    ).decode()


def _deserialize_cursor(cursor: typing.Optional[str]) -> int:
    if not cursor:
        return 0
    doc = json.loads(base64.b64decode(cursor))
    return doc['index']


def _default_segment_points(
        segment_id,
        pickup_coordinates=None,
        dropoff_coordinates=None,
        dropoff_time_intervals=None,
        return_time_intervals=None,
):
    def _make_point_id(segment_id, visit_order):
        return f'{segment_id}/{visit_order}'

    assert (pickup_coordinates is None) == (dropoff_coordinates is None)
    if pickup_coordinates is None:
        pickup_coordinates = [37.4, 55.7]
        dropoff_coordinates = [37.4, 55.7]
    return [
        Point(
            point_id=_make_point_id(segment_id, 1),
            segment_id=segment_id,
            point_type='pickup',
            coordinates=copy.copy(pickup_coordinates),
            external_order_id='1234-5678',
        ),
        Point(
            point_id=_make_point_id(segment_id, 2),
            segment_id=segment_id,
            point_type='dropoff',
            coordinates=copy.copy(dropoff_coordinates),
            time_intervals=copy.copy(dropoff_time_intervals),
        ),
        Point(
            point_id=_make_point_id(segment_id, 3),
            segment_id=segment_id,
            point_type='return',
            coordinates=copy.copy(pickup_coordinates),
            external_order_id='1234-5678',
            time_intervals=copy.copy(return_time_intervals),
        ),
    ]


def make_segment(
        *,
        taxi_classes=None,
        taxi_requirements=None,
        special_requirements=None,
        custom_context=None,
        crutches=None,
        segment_id=None,
        pickup_coordinates=None,
        dropoff_coordinates=None,
        dropoff_time_intervals=None,
        return_time_intervals=None,
        due=None,
        items=None,
        claim_features=[],
        claim_origin=None,
        **kwargs,
):
    if taxi_classes is None:
        taxi_classes = {'courier'}
    if taxi_requirements is None:
        taxi_requirements = {}
    if special_requirements is None:
        special_requirements = {}
    if custom_context is None:
        custom_context = {}
    if crutches is None:
        crutches = {}
    if segment_id is None:
        segment_id = str(uuid.uuid4())
    points = _default_segment_points(
        segment_id,
        pickup_coordinates=pickup_coordinates,
        dropoff_coordinates=dropoff_coordinates,
        dropoff_time_intervals=dropoff_time_intervals,
        return_time_intervals=return_time_intervals,
    )
    if due is not None:
        points[0].due = due
    if items is None:
        items = [
            SegmentItem(
                item_id='bf0d5230ab544d29b5dc0a785aaa169c',
                size=ItemSizes(length=0, width=0, height=0),
                weight=0,
                quantity=1,
            ),
        ]

    segment = Segment(
        points=points,
        id=segment_id,
        taxi_classes=taxi_classes,
        taxi_requirements=taxi_requirements,
        special_requirements=special_requirements,
        custom_context=custom_context,
        crutches=crutches,
        items=items,
        claim_features=claim_features,
        claim_origin=claim_origin,
        **kwargs,
    )
    return segment


def _make_points(segment_id, segment_json):
    locations = {}
    for location in segment_json['locations']:
        locations[location['id']] = location

    points = []
    for point in segment_json['points']:
        location_id = point['location_id']
        points.append(
            Point(
                segment_id=segment_id,
                point_type=point['type'],
                coordinates=locations[location_id]['coordinates'],
                external_order_id=point.get('external_order_id', None),
                due=point.get('due', None),
                point_id=point['point_id'],
                location_id=location_id,
                is_visited=False,
                is_skipped=False,
                time_intervals=point.get('time_intervals', None),
            ),
        )
    return points


def _make_items(segment_json):
    items = []
    for item in segment_json['items']:
        item_size = item.get('size', None)
        if item_size:
            size = ItemSizes(
                length=item_size['length'],
                width=item_size['width'],
                height=item_size['height'],
            )

        items.append(
            SegmentItem(
                item_id=item['item_id'],
                quantity=item['quantity'],
                size=size,
                weight=item.get('weight'),
            ),
        )
    return items


def _make_chosen_waybill(external_ref):
    return {
        'router_id': external_ref.split('/')[0],
        'external_ref': external_ref,
    }


def _parse_requirements(performer_requirements: dict):
    performer_requirements_copy = copy.deepcopy(performer_requirements)

    taxi_classes = performer_requirements_copy.pop('taxi_classes')
    special_requirements = performer_requirements_copy.pop(
        'special_requirements',
    )
    taxi_requirements = performer_requirements_copy

    return taxi_classes, special_requirements, taxi_requirements


def parse_segment(segment_json: dict, waybill_id: str = None) -> Segment:
    segment_part = segment_json['segment']
    dispatch_part = segment_json['dispatch']
    segment_id = segment_part['id']

    points = _make_points(segment_id, segment_part)
    items = _make_items(segment_part)

    (
        taxi_classes,
        special_requirements,
        taxi_requirements,
    ) = _parse_requirements(segment_part['performer_requirements'])

    chosen_waybill = None
    if waybill_id:
        chosen_waybill = _make_chosen_waybill(waybill_id)

    return Segment(
        items=items,
        points=points,
        id=segment_id,
        taxi_classes=taxi_classes,
        taxi_requirements=taxi_requirements,
        special_requirements=_parse_special_requirements(special_requirements),
        custom_context=segment_part.get('custom_context', None),
        resolution=segment_part.get('resolution', None),
        corp_client_id=segment_part.get('corp_client_id', None),
        allow_batch=segment_part['allow_batch'],
        allow_alive_batch_v1=segment_part['allow_alive_batch_v1'],
        allow_alive_batch_v2=segment_part.get('allow_alive_batch_v2', None),
        zone_id=segment_part['zone_id'],
        estimations=segment_part.get('estimations', None),
        waybill_building_version=dispatch_part['waybill_building_version'],
        waybill_building_awaited=dispatch_part['waybill_building_awaited'],
        waybill_building_deadline=dispatch_part.get(
            'waybill_building_deadline', None,
        ),
        revision=dispatch_part['revision'],
        modified_classes=dispatch_part.get('modified_classes', None),
        tariffs_substitution=dispatch_part.get('tariffs_substitution', None),
        chosen_waybill=chosen_waybill,
        crutches={},  # FIXME
        # status, planner, comment, routers - default
    )


def _merge_taxi_requirements(
        segments: typing.List[Segment],
) -> typing.Dict[str, typing.Any]:
    taxi_requirements: dict = {}
    for segment in segments:
        for requirement, value in segment.taxi_requirements.items():
            if requirement in taxi_requirements:
                assert value == taxi_requirements['value']
            else:
                taxi_requirements[requirement] = value
    return taxi_requirements


def _parse_special_requirements(special_requirements: dict) -> dict:
    special_requirements_by_classes: dict = {}
    for key, value in special_requirements.items():
        assert key == 'virtual_tariffs'
        for record in value:
            taxi_class = record['class']
            special_requirement_ids = {
                d['id'] for d in record['special_requirements']
            }
            if taxi_class in special_requirements_by_classes:
                special_requirements_by_classes[
                    taxi_class
                ] |= special_requirement_ids
            else:
                special_requirements_by_classes[
                    taxi_class
                ] = special_requirement_ids
    return special_requirements_by_classes


def serialize_special_requirements(
        special_requirements_by_classes: dict,
) -> dict:
    virtual_tariffs = []
    for (
            taxi_class,
            special_requirement_ids,
    ) in special_requirements_by_classes.items():
        virtual_tariffs.append(
            {
                'class': taxi_class,
                'special_requirements': [
                    {'id': req_id} for req_id in special_requirement_ids
                ],
            },
        )
    return {'virtual_tariffs': virtual_tariffs}


def merge_special_requirements(
        list_special_requirements: typing.List[
            typing.Dict[str, typing.Set[str]]
        ],
) -> typing.Dict[str, typing.Set[str]]:
    special_requirements_by_classes: dict = {}
    for special_requirements in list_special_requirements:
        for (
                taxi_class,
                special_requirement_ids,
        ) in special_requirements.items():
            if taxi_class in special_requirements_by_classes:
                special_requirements_by_classes[
                    taxi_class
                ] |= special_requirement_ids
            else:
                special_requirements_by_classes[
                    taxi_class
                ] = special_requirement_ids

    return special_requirements_by_classes


def _merge_taxi_classes(segments: typing.List[Segment]) -> typing.List[str]:
    taxi_classes: typing.Set[str] = set()
    for segment in segments:
        if taxi_classes:
            taxi_classes &= set(segment.taxi_classes)
        else:
            taxi_classes = set(segment.taxi_classes)
    return list(taxi_classes)


def parse_waybill(waybill_json: dict, waybill_id: str) -> Waybill:
    segments = []
    for segment_json in waybill_json['segments']:
        segments.append(
            parse_segment(
                segment_json=segment_json['segment'], waybill_id=waybill_id,
            ),
        )
    assert segments
    points = []
    for point in waybill_json['path']:
        point_added = False
        for segment in segments:
            if point['segment_id'] != segment.id:
                continue
            for segment_point in segment.points:
                if segment_point.point_id != point['point_id']:
                    continue
                points.append(segment_point)
                point_added = True
                break
            break
        assert point_added, (
            f'point not found in proposed segments, '
            f'point: {point}, segments: {segments}'
        )

    taxi_requirements = _merge_taxi_requirements(segments)
    special_requirements = serialize_special_requirements(
        merge_special_requirements([s.special_requirements for s in segments]),
    )

    taxi_classes = waybill_json.get('taxi_order_requirements', {}).get(
        'taxi_classes', None,
    )
    if not taxi_classes:
        taxi_classes = _merge_taxi_classes(segments)

    update_proposition = None
    if 'update_proposition' in waybill_json:
        update_proposition = WaybillUpdateProposition(
            previous_waybill_ref=waybill_json['update_proposition'][
                'previous_waybill_ref'
            ],
            previous_waybill_revision=waybill_json['update_proposition'][
                'previous_waybill_revision'
            ],
        )

    return Waybill(
        id=waybill_id,
        taxi_classes=taxi_classes,
        taxi_requirements=taxi_requirements,
        special_requirements=special_requirements,
        revision=waybill_json.get('revision', 1),
        segments=segments,
        points=points,
        update_proposition=update_proposition,
    )
