import dataclasses
import datetime
import typing

import pytest


@dataclasses.dataclass
class AdminSegmentReorder:
    segment_id: str
    waybill_building_version: int
    reason: str
    ticket: typing.Optional[str]
    source: typing.Optional[str]
    forced_action: typing.Optional[str]
    cancel_request_token: typing.Optional[str]
    created_at: datetime.datetime
    updated_ts: datetime.datetime


@pytest.fixture(name='prepare_admin_segment_reorder')
def _prepare_admin_segment_reorder(pgsql):
    def prepare(
            segment_id,
            waybill_building_version,
            reason='reason_1',
            ticket=None,
            source=None,
            forced_action=None,
            cancel_request_token=None,
            created_at='2020-01-01T10:00:00+00:00',
            updated_ts='2020-01-01T10:00:00+00:00',
    ):
        cursor = pgsql['cargo_dispatch'].cursor()
        cursor.execute(
            """
INSERT INTO cargo_dispatch.admin_segment_reorders (
    segment_id,
    waybill_building_version,
    reason,
    ticket,
    source,
    forced_action,
    cancel_request_token,
    created_at,
    updated_ts
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                segment_id,
                waybill_building_version,
                reason,
                ticket,
                source,
                forced_action,
                cancel_request_token,
                created_at,
                updated_ts,
            ),
        )

    return prepare


@pytest.fixture(name='fetch_admin_segment_reorder')
def _fetch_admin_segment_reorder(pgsql):
    def fetch(segment_id, waybill_building_version):
        cursor = pgsql['cargo_dispatch'].cursor()
        cursor.execute(
            """
            SELECT
                segment_id,
                waybill_building_version,
                reason,
                ticket,
                source,
                forced_action,
                cancel_request_token,
                created_at,
                updated_ts
            FROM cargo_dispatch.admin_segment_reorders
            WHERE segment_id = %s AND waybill_building_version = %s
            """,
            (segment_id, waybill_building_version),
        )
        rows = cursor.fetchall()
        if rows is None:
            raise RuntimeError(
                'admin_segment_reorder is not found'
                + f'segment_id: {segment_id}'
                + f', waybill_building_version: {waybill_building_version}',
            )
        assert len(rows) == 1
        row = rows[0]
        return AdminSegmentReorder(
            segment_id=row[0],
            waybill_building_version=row[1],
            reason=row[2],
            ticket=row[3],
            source=row[4],
            forced_action=row[5],
            cancel_request_token=row[6],
            created_at=row[7],
            updated_ts=row[8],
        )

    return fetch
