import json

NULL = 'NULL'


def transaction(sql_query):
    return f"""
BEGIN TRANSACTION;
{sql_query}
COMMIT TRANSACTION;
    """


def add_order(
        order_id,
        uid,
        depot_id,
        vendor,
        ref_order,
        status,
        token,
        delivery_at='NOW()',
        timeslot_start=None,
        timeslot_end=None,
        personal_phone_id=None,
        customer_address=None,
        customer_location=None,
        customer_meta=None,
        price=None,
        request_kind=None,
):
    if token is None:
        token = NULL
    else:
        token = f'\'{token}\''
    if timeslot_start is None:
        timeslot_start = NULL
    else:
        timeslot_start = f'\'{timeslot_start}\''
    if timeslot_end is None:
        timeslot_end = NULL
    else:
        timeslot_end = f'\'{timeslot_end}\''
    if uid is None:
        uid = NULL
    else:
        uid = f'\'{uid}\''
    if personal_phone_id is None:
        personal_phone_id = NULL
    else:
        personal_phone_id = f'\'{personal_phone_id}\''
    if customer_address is None:
        customer_address = NULL
    else:
        customer_address = f'\'{customer_address}\''
    if customer_location is None:
        customer_location = NULL
    else:
        customer_location = f'\'{customer_location}\''
    if customer_meta is None:
        customer_meta = {}
    if price is None:
        price = NULL
    if request_kind is None:
        request_kind = NULL
    else:
        request_kind = f'\'{request_kind}\''
    return f"""
INSERT INTO parcels.orders (
    id, uid, depot_id, vendor, ref_order, status, delivery_at, token,
    timeslot_start, timeslot_end, personal_phone_id, customer_address,
    customer_location, customer_meta, price, request_kind
)
VALUES
(
    '{order_id}',
    {uid},
    '{depot_id}',
    '{vendor}',
    '{ref_order}',
    '{status}',
    '{delivery_at}',
    {token},
    {timeslot_start},
    {timeslot_end},
    {personal_phone_id},
    {customer_address},
    {customer_location},
    '{customer_meta}',
    {price},
    {request_kind}
);
    """


def set_order_status(order_id, status):
    return f"""
UPDATE parcels.orders SET status = '{status}'
WHERE id = '{order_id}';
    """


def add_parcel(
        item_id,
        order_id,
        vendor,
        measurements,
        status,
        barcode=None,
        partner_id=None,
        wms_id=None,
        description=None,
        status_meta=None,
        in_stock_quantity=None,
):
    if barcode is None:
        barcode = NULL
    else:
        barcode = f'\'{barcode}\''
    if partner_id is None:
        partner_id = NULL
    else:
        partner_id = f'\'{partner_id}\''
    if wms_id is None:
        wms_id = NULL
    else:
        wms_id = f'\'{wms_id}\''
    if description is None:
        description = NULL
    else:
        description = f'\'{description}\''
    if status_meta is None:
        status_meta = {}
    if in_stock_quantity is None:
        in_stock_quantity = 0
    return f"""
INSERT INTO parcels.items (
    id, order_id, vendor, barcode, partner_id, wms_id, measurements,
    description, status, status_meta, in_stock_quantity
)
VALUES
(
    '{item_id}',
    '{order_id}',
    '{vendor}',
    {barcode},
    {partner_id},
    {wms_id},
    '{measurements}'::parcels.item_measurements_t,
    {description},
    '{status}',
    '{status_meta}',
    '{in_stock_quantity}'
);
    """


def select_parcel(item_id):
    return f"""
SELECT id, order_id, vendor, barcode, partner_id, wms_id, measurements, status,
       status_meta, in_stock_quantity, updated
FROM parcels.items
WHERE id = '{item_id}';
    """


def set_parcel_status(item_id, status, status_meta=None):
    if status_meta is None:
        status_meta = {}
    return f"""
UPDATE parcels.items SET status = '{status}', status_meta = '{status_meta}'
WHERE id = '{item_id}';
    """


def select_order(order_id):
    return f"""
SELECT id, uid, depot_id, vendor, ref_order, status, updated,
       timeslot_start, timeslot_end, request_kind
FROM parcels.orders
WHERE id = '{order_id}';
    """


def set_order_updated(order_id, timestamp):
    return f"""
ALTER TABLE parcels.orders DISABLE TRIGGER orders_updated;
UPDATE parcels.orders SET updated = '{timestamp.isoformat()}'
    WHERE id = '{order_id}';
ALTER TABLE parcels.orders ENABLE TRIGGER orders_updated;
"""


def set_parcel_updated(parcel_id, timestamp):
    return f"""
ALTER TABLE parcels.items DISABLE TRIGGER items_updated;
UPDATE parcels.items SET updated = '{timestamp.isoformat()}'
    WHERE id = '{parcel_id}';
ALTER TABLE parcels.items ENABLE TRIGGER items_updated;
"""


def insert_order_dispatch_schedule(
        order_id,
        dispatch_start,
        dispatch_end,
        dispatched=False,
        dispatch_id=None,
):
    if dispatch_id is None:
        dispatch_id = NULL
    else:
        dispatch_id = f'\'{dispatch_id}\''
    return f"""
INSERT INTO parcels.orders_dispatch_schedule (
    order_id,
    dispatch_start,
    dispatch_end,
    dispatched,
    dispatch_id
)
VALUES (
    '{order_id}',
    '{dispatch_start}',
    '{dispatch_end}',
    {dispatched},
    {dispatch_id}
);
"""


def insert_deffered_acceptance(
        item_id,
        real_acceptance_time='NOW()',
        new_acceptance_time=None,
        accepted=False,
):
    if new_acceptance_time is None:
        new_acceptance_time = NULL
    else:
        new_acceptance_time = f'\'{new_acceptance_time}\''
    return f"""
INSERT INTO parcels.deffered_acceptance (
    item_id,
    real_acceptance_time,
    new_acceptance_time,
    accepted
)
VALUES (
'{item_id}',
'{real_acceptance_time}',
{new_acceptance_time},
{accepted}
);
"""


def flush_distlocks():
    return """
TRUNCATE TABLE parcels.distlocks;
TRUNCATE TABLE parcels.distlock_periodic_updates;
"""


def insert_items_history(item_id, status, order_id, updated=None):
    meta = {'order_id': order_id}
    return f"""
INSERT INTO parcels.items_history (item_id, status, updated, meta)
VALUES (
'{item_id}',
'{status}',
'{updated if updated is not None else "2021-10-26T13:28:36.347916+00:00"}',
'{json.dumps(meta)}'
);
"""
