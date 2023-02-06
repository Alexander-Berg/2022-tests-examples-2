import dataclasses
import datetime
import typing


@dataclasses.dataclass
class PointAction:
    cargo_order_id: str
    taxi_order_id: str
    waybill_ref: str
    segment_id: str
    claim_point_id: int
    claim_id: str
    corp_client_id: typing.Optional[str]
    zone_id: str
    park_id: str
    driver_id: str
    action_type: str
    reason_type: str
    admin_login: str
    ticket: str
    text_reason: typing.Optional[str]
    is_reorder_disabled_by_admin: bool
    reorder_or_cancel_type: typing.Optional[str]
    is_cancelled_paid_waiting: bool
    is_cancelled_paid_arriving: bool
    is_fine_required: bool
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


POINT_ACTION_COLUMNS = """
        cargo_order_id,
        taxi_order_id,
        waybill_ref,
        segment_id,
        claim_point_id,
        claim_id,
        corp_client_id,
        zone_id,
        park_id,
        driver_id,
        action_type,
        reason_type,
        admin_login,
        ticket,
        text_reason,
        is_reorder_disabled_by_admin,
        reorder_or_cancel_type,
        is_cancelled_paid_waiting,
        is_cancelled_paid_arriving,
        is_fine_required,
        status,
        created_at,
        updated_at
    """


def insert_point_action(
        pgsql,
        waybill_ref,
        claim_point_id,
        action_type,
        reason_type,
        *,
        cargo_order_id='11111111-1111-1111-1111-111111111111',
        taxi_order_id='taxi_order_id_1',
        segment_id='segment_id_1',
        claim_id='claim_id_1',
        corp_client_id='corp_client_id_1',
        zone_id='zone_id_1',
        park_id='park_id_1',
        driver_id='driver_id_1',
        admin_login='admin_login_1',
        ticket='ticket_1',
        text_reason='text reason',
        is_reorder_disabled_by_admin=False,
        reorder_or_cancel_type=None,
        is_cancelled_paid_waiting=False,
        is_cancelled_paid_arriving=False,
        is_fine_required=False,
        status='in_progress',
        created_at='2020-01-01T10:00:00+00:00',
        updated_at='2020-01-01T10:00:00+00:00',
):
    cursor = pgsql['cargo_support'].cursor()
    cursor.execute(
        """INSERT INTO cargo_support.point_actions ("""
        + POINT_ACTION_COLUMNS
        + """)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s)
        """,
        (
            cargo_order_id,
            taxi_order_id,
            waybill_ref,
            segment_id,
            claim_point_id,
            claim_id,
            corp_client_id,
            zone_id,
            park_id,
            driver_id,
            action_type,
            reason_type,
            admin_login,
            ticket,
            text_reason,
            is_reorder_disabled_by_admin,
            reorder_or_cancel_type,
            is_cancelled_paid_waiting,
            is_cancelled_paid_arriving,
            is_fine_required,
            status,
            created_at,
            updated_at,
        ),
    )


def create_point_action_from_row(row):
    return PointAction(
        cargo_order_id=row[0],
        taxi_order_id=row[1],
        waybill_ref=row[2],
        segment_id=row[3],
        claim_point_id=row[4],
        claim_id=row[5],
        corp_client_id=row[6],
        zone_id=row[7],
        park_id=row[8],
        driver_id=row[9],
        action_type=row[10],
        reason_type=row[11],
        admin_login=row[12],
        ticket=row[13],
        text_reason=row[14],
        is_reorder_disabled_by_admin=row[15],
        reorder_or_cancel_type=row[16],
        is_cancelled_paid_waiting=row[17],
        is_cancelled_paid_arriving=row[18],
        is_fine_required=row[19],
        status=row[20],
        created_at=row[21],
        updated_at=row[22],
    )


def select_point_action(pgsql, waybill_ref, claim_point_id, action_type):
    cursor = pgsql['cargo_support'].cursor()
    cursor.execute(
        """SELECT """
        + POINT_ACTION_COLUMNS
        + """ FROM cargo_support.point_actions
        WHERE waybill_ref = %s AND claim_point_id = %s AND action_type = %s
        """,
        (waybill_ref, claim_point_id, action_type),
    )
    rows = cursor.fetchall()
    if rows is None:
        raise RuntimeError(
            'point_action is not found'
            + f'waybill_ref: {waybill_ref}'
            + f', claim_point_id: {claim_point_id}'
            + f', action_type: {action_type}',
        )
    assert len(rows) == 1
    return create_point_action_from_row(rows[0])


def select_point_actions(pgsql, waybill_ref):
    cursor = pgsql['cargo_support'].cursor()
    cursor.execute(
        """SELECT """
        + POINT_ACTION_COLUMNS
        + """ FROM cargo_support.point_actions
        WHERE waybill_ref = %s
        ORDER BY claim_point_id, action_type
        """,
        (waybill_ref,),
    )
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append(create_point_action_from_row(row))

    return result
