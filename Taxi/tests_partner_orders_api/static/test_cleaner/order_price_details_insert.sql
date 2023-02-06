INSERT INTO partner_orders_api.order_price_details
  (
  order_id,
  details_set_id,
  calculated_at
  )
VALUES
  (
    'order_id_1',
    'details_set_id_1',
    NOW()
),
  (
    'order_id_2',
    'details_set_id_2',
    NOW() + ('1 hour')
::interval
);

INSERT INTO partner_orders_api.price_details_items
  (
  details_set_id,
  price,
  item_name
  )
VALUES
  (
    'details_set_id_1',
    10.1,
    'item_name_1'
),
  (
    'details_set_id_1',
    20.1,
    'item_name_2'
),
  (
    'details_set_id_2',
    30.1,
    'item_name_3'
);
