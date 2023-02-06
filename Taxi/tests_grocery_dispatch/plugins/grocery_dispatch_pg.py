# flake8: noqa IS001
# pylint: disable=import-only-modules, invalid-name, protected-access

from abc import abstractmethod
import ast
from datetime import datetime, timezone, timedelta
from functools import partial
from typing import (
    Any,
    Dict,
    Generic,
    List,
    NewType,
    Optional,
    TypeVar,
    Callable,
)
from uuid import UUID

import psycopg2.extras
import psycopg2.extensions
import pytest

from tests_grocery_dispatch.plugins import sql_queries as queries
from tests_grocery_dispatch.plugins.models import (
    CargoClaim,
    DispatchExtraInfo,
    DispatchInfo,
    OrderInfo,
    PerformerInfo,
    Status,
    StatusMeta,
    Point,
    RescheduleState,
)
from tests_grocery_dispatch.plugins.utils import as_json, proxy_property

PgCluster = Any
CargoModelT = Any
DispatchModelT = Any
RescheduleStateModelT = Any
T = TypeVar('T')
_proxy_field = partial(proxy_property, '_wrapped')


class Persistence(Generic[T]):
    _wrapped: T
    _cluster: PgCluster
    auto_refresh: bool
    auto_save: bool

    def __init__(self, cluster: PgCluster, wrapped: T):
        self._cluster = cluster
        self._wrapped = wrapped
        self.auto_refresh = True
        self.auto_save = True
        self._auto_save_saved = self.auto_save
        self._auto_refresh_saved = self.auto_refresh

    def disable_auto(self):
        self.save_auto()
        self.auto_save = False
        self.auto_refresh = False

    def save_auto(self):
        self._auto_save_saved = self.auto_save
        self._auto_refresh_saved = self.auto_refresh

    def restore_auto(self):
        self.auto_refresh = self._auto_refresh_saved
        self.auto_save = self._auto_save_saved

    @abstractmethod
    def insert(self):
        ...

    @abstractmethod
    def refresh(self):
        ...

    @abstractmethod
    def save(self):
        ...

    def __eq__(self, other):
        self.refresh()
        if isinstance(other, Persistence):
            other.refresh()
            return self._wrapped == other._wrapped
        if isinstance(other, type(self._wrapped)):
            return self._wrapped == other

        raise NotImplementedError()


class DispatchExtraPersistenceMixin(Persistence[DispatchExtraInfo]):
    def __init__(self, cluster, **kwargs):
        super().__init__(cluster, DispatchExtraInfo(**kwargs))

    def insert(self):
        self.disable_auto()
        self._cluster.cursor().execute(
            queries.INSERT_EXTRA_SQL,
            (
                self._wrapped.dispatch_id,
                self._wrapped.eta_timestamp,
                self._wrapped.smoothed_eta_timestamp,
                self._wrapped.smoothed_eta_eval_time,
                self._wrapped.result_eta_timestamp,
                self._wrapped.heuristic_polyline_eta_ts,
                self._wrapped.performer_position,
                self._wrapped.pickup_eta_seconds,
                self._wrapped.deliver_prev_eta_seconds,
                self._wrapped.deliver_current_eta_seconds,
                self._wrapped.smoothed_heuristic_eval_time,
                self._wrapped.smoothed_heuristic_eta_ts,
            ),
        )
        self.restore_auto()

    def save(self):
        self.disable_auto()
        self._cluster.cursor().execute(
            queries.UPDATE_EXTRA_SQL,
            {
                'dispatch_id': self._wrapped.dispatch_id,
                'eta_timestamp': self._wrapped.eta_timestamp,
                'smoothed_eta_timestamp': self._wrapped.smoothed_eta_timestamp,
                'smoothed_eta_eval_time': self._wrapped.smoothed_eta_eval_time,
                'result_eta_timestamp': self._wrapped.result_eta_timestamp,
                'heuristic_polyline_eta_ts': (
                    self._wrapped.heuristic_polyline_eta_ts
                ),
                'performer_position': self._wrapped.performer_position,
                'pickup_eta_seconds': self._wrapped.pickup_eta_seconds,
                'deliver_prev_eta_seconds': (
                    self._wrapped.deliver_prev_eta_seconds
                ),
                'deliver_current_eta_seconds': (
                    self._wrapped.deliver_current_eta_seconds
                ),
                'smoothed_heuristic_eval_time': (
                    self._wrapped.smoothed_heuristic_eval_time
                ),
                'smoothed_heuristic_eta_ts': (
                    self._wrapped.smoothed_heuristic_eta_ts
                ),
            },
        )
        self.restore_auto()

    def refresh(self):
        self.disable_auto()
        cursor = self._cluster.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor,
        )
        cursor.execute(queries.SELECT_EXTRA_SQL, (self.dispatch_id,))
        row = cursor.fetchone()
        cursor.close()

        self._wrapped.dispatch_id = row.dispatch_id
        self._wrapped.eta_timestamp = row.eta_timestamp
        self._wrapped.smoothed_eta_timestamp = row.smoothed_eta_timestamp
        self._wrapped.smoothed_eta_eval_time = row.smoothed_eta_eval_time
        self._wrapped.result_eta_timestamp = row.result_eta_timestamp
        self._wrapped.heuristic_polyline_eta_ts = row.heuristic_polyline_eta_ts
        self._wrapped.performer_position = row.performer_position
        self._wrapped.pickup_eta_seconds = row.pickup_eta_seconds
        self._wrapped.deliver_prev_eta_seconds = row.deliver_prev_eta_seconds
        self._wrapped.deliver_current_eta_seconds = (
            row.deliver_current_eta_seconds
        )
        self._wrapped.smoothed_heuristic_eval_time = (
            row.smoothed_heuristic_eval_time
        )
        self._wrapped.smoothed_heuristic_eta_ts = row.smoothed_heuristic_eta_ts
        self.restore_auto()


class DispatchPersistenceMixin(Persistence[DispatchInfo]):
    def __init__(self, cluster, **kwargs):
        super().__init__(cluster, DispatchInfo(**kwargs))

    def insert(self: DispatchModelT):
        self.disable_auto()
        self._cluster.cursor().execute(
            queries.INSERT_DISPATCHES_SQL,
            (
                self.dispatch_id,
                self.order_id,
                self.performer_id,
                self.dispatch_name,
                self.version,
                self.status,
                self.status_updated,
                as_json(self._wrapped.order),
                as_json(self._wrapped.performer),
                as_json(self._wrapped.status_meta),
                self._wrapped.wave,
            ),
        )
        self.restore_auto()

    def save(self: DispatchModelT):
        self.disable_auto()
        self._cluster.cursor().execute(
            queries.UPDATE_DISPATCHES_SQL,
            {
                'dispatch_id': self.dispatch_id,
                'order_id': self.order_id,
                'performer_id': self.performer_id,
                'dispatch_type': self.dispatch_name,
                'status': self.status,
                'status_updated': self.status_updated,
                'order_info': as_json(self._wrapped.order),
                'performer_info': as_json(self._wrapped.performer),
                'status_meta': as_json(self._wrapped.status_meta),
                'wave': self._wrapped.wave,
                'eta': 0,
            },
        )
        self.restore_auto()

    def refresh(self: DispatchModelT):
        cursor = self._cluster.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor,
        )
        cursor.execute(
            queries.SELECT_DISPATCHES_SQL, (self._wrapped.dispatch_id,),
        )
        row = cursor.fetchone()
        cursor.close()

        self._wrapped = self.parse_from_record(row)

    @staticmethod
    def parse_from_record(item):
        return DispatchInfo(
            dispatch_id=item.id,
            dispatch_name=item.dispatch_type,
            version=item.version,
            status=item.status,
            status_updated=item.status_updated.astimezone(timezone.utc),
            order=OrderInfo(**item.order_info),
            performer=item.performer_info,
            status_meta=item.status_meta,
            wave=item.wave,
            eta=item.eta,
            failure_reason_type=item.failure_reason_type,
        )

    def history(self: DispatchModelT) -> List[DispatchInfo]:
        cursor = self._cluster.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor,
        )
        cursor.execute(
            queries.SELECT_DISPATCHES_HISTORY_UPDATED_SQL,
            (self._wrapped.dispatch_id,),
        )
        res = []
        for item in cursor.fetchall():
            res.append(self.parse_from_record(item))
        return res

    def delete(self: DispatchModelT) -> None:
        cursor = self._cluster.cursor()
        cursor.execute(
            queries.DELETE_DISPATCHES_SQL, (self._wrapped.dispatch_id,),
        )


class CargoPersistenceMixin(Persistence[CargoClaim]):
    def __init__(self, cluster, **kwargs):
        super().__init__(cluster, CargoClaim(**kwargs))

    def insert(self: CargoModelT):
        self.disable_auto()
        self._cluster.cursor().execute(
            queries.INSERT_CARGO_CLAIM_SQL,
            (
                str(self.dispatch_id),
                self.claim_id,
                self.is_current_claim,
                self.claim_status,
                self.claim_version,
                self.auth_token_key,
                self.wave,
                self.order_location,
            ),
        )
        self.restore_auto()

    def save(self):
        ...

    def refresh(self: CargoModelT):
        self.disable_auto()
        cursor = self._cluster.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor,
        )
        cursor.execute(
            queries.GET_CARGO_CLAIM_BY_CLAIM_ID_SQL, (self.claim_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        assert row, 'Empty result from database'

        self._wrapped.dispatch_id = row.dispatch_id
        self._wrapped.claim_id = row.claim_id
        self._wrapped.is_current_claim = row.is_current_claim
        self._wrapped.claim_status = row.claim_status
        self._wrapped.claim_version = row.claim_version
        self._wrapped.auth_token_key = row.auth_token_key
        self._wrapped.wave = row.wave
        self._wrapped.order_location = row.order_location
        self.restore_auto()


class RescheduleStateMixin(Persistence[RescheduleState]):
    def __init__(self, cluster, **kwargs):
        super().__init__(cluster, RescheduleState(**kwargs))

    def insert(self):
        ...

    def refresh(self: RescheduleStateModelT):
        cursor = self._cluster.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor,
        )
        cursor.execute(
            queries.GET_RESCHEDULE_STATE, (self._wrapped.dispatch_id,),
        )
        row = cursor.fetchone()
        cursor.close()

        self._wrapped.dispatch_id = row.dispatch_id
        self._wrapped.idempotency_token = row.idempotency_token
        self._wrapped.wave = row.wave
        self._wrapped.options = row.options
        self._wrapped.status = row.status

    def save(self):
        ...


class DispatchModel(DispatchPersistenceMixin):
    dispatch_id: str = _proxy_field()
    order_id: str = _proxy_field('order')
    performer_id: Optional[str] = _proxy_field('performer')
    performer: Optional[PerformerInfo] = _proxy_field()
    dispatch_name: str = _proxy_field()
    version: int = _proxy_field()
    order: OrderInfo = _proxy_field()
    failure_reason_type: str = _proxy_field()
    status_meta: StatusMeta = _proxy_field()
    status: Status = _proxy_field()
    status_updated: datetime = _proxy_field()
    wave: int = _proxy_field()


class DispatchExtraModel(DispatchExtraPersistenceMixin):
    dispatch_id: UUID = _proxy_field()
    eta_timestamp: Optional[datetime] = _proxy_field()
    smoothed_eta_timestamp: Optional[datetime] = _proxy_field()
    smoothed_eta_eval_time: Optional[datetime] = _proxy_field()
    result_eta_timestamp: Optional[datetime] = _proxy_field()
    heuristic_polyline_eta_ts: Optional[datetime] = _proxy_field()
    performer_position: Optional[Point] = _proxy_field()
    pickup_eta_seconds: Optional[timedelta] = _proxy_field()
    deliver_prev_eta_seconds: Optional[timedelta] = _proxy_field()
    deliver_current_eta_seconds: Optional[timedelta] = _proxy_field()
    smoothed_heuristic_eval_time: Optional[datetime] = _proxy_field()
    smoothed_heuristic_eta_ts: Optional[datetime] = _proxy_field()


class CargoModel(CargoPersistenceMixin):
    dispatch_id: UUID = _proxy_field()
    claim_id: str = _proxy_field()
    is_current_claim: bool = _proxy_field()
    claim_status: str = _proxy_field()
    claim_version: int = _proxy_field()
    auth_token_key: Optional[str] = _proxy_field()
    wave: int = _proxy_field()
    order_location: Point = _proxy_field()


class RescheduleStateModel(RescheduleStateMixin):
    dispatch_id: str = _proxy_field()
    idempotency_token: str = _proxy_field()
    wave: int = _proxy_field()
    options: Optional[Dict] = _proxy_field()
    status: str = _proxy_field()


def adapt_point(point: Point):
    return psycopg2.extensions.AsIs(('({}, {})'.format(point.lon, point.lat)))


def cast_point(value, cur):
    if value is None:
        return None
    obj = ast.literal_eval(value)
    return Point(*obj)


def get_pg_type_oid(pgsql, schema: str, type_name: str) -> int:
    cur = pgsql['grocery_dispatch'].cursor()
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
    psycopg2.extensions.register_adapter(Point, adapting)


@pytest.fixture(name='register_types')
def register_types_(pgsql):
    register_type(pgsql, 'dispatch', 'location', cast_point, adapt_point)


@pytest.fixture(name='cargo_pg')
def _cargo_pg(pgsql, register_types):
    cluster = pgsql['grocery_dispatch']

    class Context:
        def __init__(self):
            pass

        @staticmethod
        def create_claim(**kwargs):
            cargo_model = CargoModel(cluster, **kwargs)
            cargo_model.insert()
            return cargo_model

        @staticmethod
        def get_claim(claim_id):
            cargo_model = CargoModel(cluster, claim_id=claim_id)
            cargo_model.refresh()
            return cargo_model

    context = Context()

    return context


@pytest.fixture(name='grocery_dispatch_pg')
def _grocery_dispatch_pg(pgsql):
    cluster = pgsql['grocery_dispatch']

    class Context:
        @staticmethod
        def create_dispatch(**kwargs):
            # Save depot in depot cache
            order = kwargs.get('order', None) or OrderInfo()
            kwargs['order'] = order
            dispatch = DispatchModel(cluster, **kwargs)
            dispatch.insert()
            return dispatch

        @staticmethod
        def get_dispatch(dispatch_id):
            dispatch = DispatchModel(cluster, dispatch_id=dispatch_id)
            dispatch.refresh()
            return dispatch

    context = Context()

    return context


@pytest.fixture(name='grocery_dispatch_extra_pg')
def grocery_dispatch_extra_pg(pgsql, register_types):
    cluster = pgsql['grocery_dispatch']

    class Context:
        @staticmethod
        def create_dispatch_extra(**kwargs):
            extra_info = DispatchExtraModel(cluster, **kwargs)
            extra_info.insert()
            return extra_info

    context = Context()

    return context


@pytest.fixture(name='grocery_reschedule_state_pg')
def grocery_reschedule_state_pg(pgsql):
    cluster = pgsql['grocery_dispatch']

    class Context:
        @staticmethod
        def get_state(**kwargs):
            reschedule_state = RescheduleStateModel(cluster, **kwargs)
            reschedule_state.refresh()
            return reschedule_state

    context = Context()

    return context
