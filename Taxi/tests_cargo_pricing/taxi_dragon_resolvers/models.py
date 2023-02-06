import dataclasses
import typing
import uuid

from tests_cargo_pricing import utils as global_utils

NOW = global_utils.from_start(minutes=0)


class Resolution:
    CANCELLED_BY_CLIENT = {
        'resolution': 'cancelled_by_client',
        'resolved_at': NOW,
    }
    FAILED_BY_PERFORMER = {
        'resolution': 'failed_by_performer',
        'resolved_at': NOW,
    }
    COMPLETED = {'resolution': 'completed', 'resolved_at': NOW}


class PaymentMethod:
    CARD = {'type': 'card'}
    CORP = {'type': 'corp'}


class PriceFor:
    CLIENT = 'client'
    PERFORMER = 'performer'


class Performer:
    FIRST = {
        'driver_id': 'uuid0',
        'park_db_id': 'dbid0',
        'assigned_at': global_utils.from_start(minutes=0),
    }

    SECOND = {
        'driver_id': 'uuid1',
        'park_db_id': 'dbid1',
        'assigned_at': global_utils.from_start(minutes=2),
    }

    THIRD = {
        'driver_id': 'uuid2',
        'park_db_id': 'dbid2',
        'assigned_at': global_utils.from_start(minutes=4),
    }


class CalcKind:
    OFFER = 'offer'
    FINAL = 'final'


@dataclasses.dataclass()
class Segment:
    # pylint: disable=invalid-name
    id: str
    payment_info: dict
    taxi_order_id: typing.Optional[str]
    resolution: typing.Optional[dict]


@dataclasses.dataclass()
class Waybill:
    taxi_order_id: str
    segments: typing.List[Segment]
    resolution: typing.Optional[dict]

    def add_segment(self, segment: Segment):
        segment.taxi_order_id = self.taxi_order_id
        self.segments.append(segment)


def make_waybill(resolution: typing.Optional[dict] = None) -> Waybill:
    return Waybill(
        taxi_order_id=uuid.uuid4().hex, segments=[], resolution=resolution,
    )


def make_segment(
        payment_info: dict, resolution: typing.Optional[dict] = None,
) -> Segment:
    return Segment(
        id=uuid.uuid4().hex,
        payment_info=payment_info,
        resolution=resolution,
        taxi_order_id=None,
    )
