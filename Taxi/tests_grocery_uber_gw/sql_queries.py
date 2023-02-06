SQL_REQUEST = """
INSERT INTO grocery_uber_gw.orders_correspondence
    (uber_order_id, grocery_order_id, delivery_status, grocery_depot_id)
VALUES ('{}', '{}', {}, {})
"""


def insert_order(
        uber_order_id, grocery_order_id, delivery_status=None, depot_id=None,
):
    delivery_status = (
        'NULL' if delivery_status is None else f'\'{delivery_status}\''
    )
    depot_id = 'NULL' if depot_id is None else f'\'{depot_id}\''
    return SQL_REQUEST.format(
        uber_order_id, grocery_order_id, delivery_status, depot_id,
    )
