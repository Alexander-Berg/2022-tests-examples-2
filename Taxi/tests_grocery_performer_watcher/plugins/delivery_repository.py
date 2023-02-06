# pylint: disable=import-only-modules, unsubscriptable-object, invalid-name
# flake8: noqa IS001
import ast
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Callable
from uuid import UUID, uuid4

import psycopg2
import pytest


class DeliveryStatus(str, Enum):
    NEW = 'new'
    PICKUPING = 'pickuping'
    DELIVERING = 'delivering'
    DELIVERY_ARRIVED = 'delivery_arrived'
    RETURNING = 'returning'
    FINISHED = 'finished'


@dataclass
class Point:
    Lon: float
    Lat: float

    @property
    def coords(self):
        return [self.Lon, self.Lat]


@dataclass
class DeliveryPoint:
    id: int
    point: Point


@dataclass
class Delivery:
    waybill_ref: str
    performer_id: str
    depot_id: str
    status: DeliveryStatus
    status_ts: Optional[datetime] = None
    version: int = 0
    id: UUID = field(default_factory=uuid4)
    prev_point: Optional[DeliveryPoint] = None
    next_point: Optional[DeliveryPoint] = None
    next_after_next_point: Optional[DeliveryPoint] = None
    radius_ts: Optional[datetime] = None
    transport_type: Optional[str] = None
    is_pull_dispatch: Optional[bool] = None


def adapt_delivery_point(point: DeliveryPoint):
    return psycopg2.extensions.AsIs(
        (point.id, '{{{}, {}}}'.format(point.point.Lon, point.point.Lat)),
    )


def cast_delivery_point(value, cur):
    if value is None:
        return None
    obj = ast.literal_eval(value)
    pos = ast.literal_eval(obj[1])

    return DeliveryPoint(obj[0], Point(*pos))


class DeliveryRepository:
    def __init__(self, pgsql):
        self._cursor = pgsql['grocery_performer_watcher'].cursor(
            cursor_factory=psycopg2.extras.RealDictCursor,
        )

    def add(self, delivery: Delivery) -> None:
        self._cursor.execute(
            'INSERT into performer_watcher.deliveries(id, waybill_ref, performer_id, depot_id, '
            'status, status_ts, version, prev_point, next_point, next_after_next_point, radius_ts, transport_type, is_pull_dispatch) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '
            'ON CONFLICT (performer_id, waybill_ref) DO UPDATE SET '
            'id = excluded.id,'
            'waybill_ref = excluded.waybill_ref,'
            'performer_id = excluded.performer_id,'
            'depot_id = excluded.depot_id,'
            'status = excluded.status,'
            'status_ts = excluded.status_ts,'
            'version  = excluded.version,'
            'prev_point = excluded.prev_point,'
            'next_point = excluded.next_point,'
            'next_after_next_point = excluded.next_after_next_point,'
            'radius_ts = excluded.radius_ts,'
            'transport_type = excluded.transport_type,'
            'is_pull_dispatch = excluded.is_pull_dispatch',
            (
                delivery.id,
                delivery.waybill_ref,
                delivery.performer_id,
                delivery.depot_id,
                delivery.status,
                delivery.status_ts,
                delivery.version,
                delivery.prev_point,
                delivery.next_point,
                delivery.next_after_next_point,
                delivery.radius_ts,
                delivery.transport_type,
                delivery.is_pull_dispatch,
            ),
        )

    def fetch_by_performer_id(self, performer_id) -> Optional[Delivery]:
        self._cursor.execute(
            'SELECT id, waybill_ref, performer_id, depot_id, '
            'status, status_ts, version, prev_point, next_point, next_after_next_point, radius_ts, transport_type, is_pull_dispatch '
            'FROM performer_watcher.deliveries '
            'WHERE performer_id = %s',
            (performer_id,),
        )
        row = self._cursor.fetchone()
        if row is None:
            return None
        return Delivery(
            id=row['id'],
            waybill_ref=row['waybill_ref'],
            performer_id=row['performer_id'],
            depot_id=row['depot_id'],
            status=row['status'],
            status_ts=row['status_ts'],
            version=row['version'],
            prev_point=row['prev_point'],
            next_point=row['next_point'],
            next_after_next_point=row['next_after_next_point'],
            radius_ts=row['radius_ts'],
            transport_type=row['transport_type'],
            is_pull_dispatch=row['is_pull_dispatch'],
        )

    def fetch_by_performer_id_and_waybill_ref(
            self, performer_id: str, waybill_ref: str,
    ) -> Optional[Delivery]:
        self._cursor.execute(
            'SELECT id, waybill_ref, performer_id, depot_id, '
            'status, status_ts, version, prev_point, next_point, next_after_next_point, radius_ts, transport_type, is_pull_dispatch '
            'FROM performer_watcher.deliveries '
            'WHERE performer_id = %s AND waybill_ref = %s',
            (performer_id, waybill_ref),
        )
        row = self._cursor.fetchone()
        if row is None:
            return None
        return Delivery(
            id=row['id'],
            waybill_ref=row['waybill_ref'],
            performer_id=row['performer_id'],
            depot_id=row['depot_id'],
            status=row['status'],
            status_ts=row['status_ts'],
            version=row['version'],
            prev_point=row['prev_point'],
            next_point=row['next_point'],
            next_after_next_point=row['next_after_next_point'],
            radius_ts=row['radius_ts'],
            transport_type=row['transport_type'],
            is_pull_dispatch=row['is_pull_dispatch'],
        )


def get_pg_type_oid(pgsql, schema: str, type_name: str) -> int:
    cur = pgsql['grocery_performer_watcher'].cursor()
    cur.execute(
        """
        SELECT pg_type.oid
        FROM pg_type JOIN pg_namespace
             ON typnamespace = pg_namespace.oid
        WHERE typname = %(typename)s
        AND nspname = %(namespace)s""",
        {'typename': type_name, 'namespace': schema},
    )
    return cur.fetchone()[0]


def register_type(
        pgsql, schema, type_name, casting: Callable, adapting: Callable,
) -> None:
    point_oid = get_pg_type_oid(pgsql, schema, type_name)
    new_type = psycopg2.extensions.new_type(
        (point_oid,), f'{schema}.{type_name}', casting,
    )
    psycopg2.extensions.register_type(new_type)
    psycopg2.extensions.register_adapter(DeliveryPoint, adapting)


@pytest.fixture(name='register_types')
def register_types_(pgsql):
    psycopg2.extras.register_uuid()
    register_type(
        pgsql,
        'performer_watcher',
        'delivery_point_v1',
        cast_delivery_point,
        adapt_delivery_point,
    )


@pytest.fixture(name='deliveries')
def deliveries_(pgsql, register_types):
    return DeliveryRepository(pgsql)
