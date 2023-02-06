INSERT INTO cargo_orders.orders (order_id, updated)
VALUES ('6776feef-01bb-400c-ab48-840fc00e0691'::UUID,
        '2020-02-20T15:55:01+03:00'::timestamptz),
       ('6776feef-01bb-400c-ab48-840fc00e0692'::UUID,
        '2020-02-20T15:55:01+03:00'::timestamptz),
        ('6776feef-01bb-400c-ab48-840fc00e0693'::UUID,
        '2020-02-28T15:55:01.4183+03:00'::timestamptz),
        ('6776feef-01bb-400c-ab48-840fc00e0698'::UUID,
        '2020-03-25T15:55:01+03:00'::timestamptz);

INSERT INTO cargo_orders.orders_performers (order_id, updated_ts)
VALUES ('6776feef-01bb-400c-ab48-840fc00e0691'::UUID,
        '2020-02-20T15:55:01+03:00'::timestamptz),
       ('6776feef-01bb-400c-ab48-840fc00e0692'::UUID,
        '2020-02-20T15:55:01+03:00'::timestamptz),
        ('6776feef-01bb-400c-ab48-840fc00e0698'::UUID,
        '2020-03-25T15:55:01+03:00'::timestamptz);

--- insert trigger workaround
UPDATE cargo_orders.orders
SET updated = '2020-02-20T15:55:01+03:00'::timestamptz
WHERE order_id IN (
  '6776feef-01bb-400c-ab48-840fc00e0691'::UUID,
  '6776feef-01bb-400c-ab48-840fc00e0692'::UUID
);
UPDATE cargo_orders.orders
SET updated = '2020-03-25T15:55:01+03:00'::timestamptz
WHERE order_id = '6776feef-01bb-400c-ab48-840fc00e0698'::UUID;
