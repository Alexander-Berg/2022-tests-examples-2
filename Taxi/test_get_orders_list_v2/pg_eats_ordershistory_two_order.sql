INSERT INTO eats_ordershistory.orders (
    order_id, order_source, eats_user_id, taxi_user_id, yandex_uid,
    place_id, status, delivery_location, total_amount, is_asap,
    cancel_reason, created_at, delivered_at, cancelled_at, ready_to_delivery_at, taken_at
) VALUES ('order-id-1', 'eda', 1, NULL, NULL, 123, 'finished', '(1,1)',
          '123.45', True, NULL, '2021-07-20T12:01:00Z', NULL, NULL, NULL, NULL),
         ('order-id-2', 'eda', 1, NULL, NULL, 456, 'cancelled', '(1,1)',
          '123.45', True, 'reason1', '2021-07-25T12:01:00Z', NULL, '2021-07-25T13:01:00Z', NULL, NULL);

INSERT INTO eats_ordershistory.cart_items(
    order_id, place_menu_item_id, name, quantity, origin_id,
    catalog_type, original_quantity, measure_unit, parent_origin_id, cost_for_customer,
    refunded_amount, weight, original_weight
)
VALUES ('order-id-1', 1, 'eda-item', 1, '1', 'core_catalog', '2', 'count',
        NULL, '1.00', '1', '1.00', '0.5'),
       ('order-id-1', 2, 'eda-item', 1, '2', 'core_catalog', '2', 'count',
        NULL, '1.00', '1', '1.00', '0.5'),
       ('order-id-1', 3, 'eda-item', 1, '3', 'core_catalog', '2', 'count',
        NULL, '1.00', '1', '1.00', '0.5'),
       ('order-id-2', 1, 'eda-item', 1, '1', 'core_catalog', '2', 'count',
        NULL, '1.00', '1', '1.00', '0.5'),
       ('order-id-2', 2, 'eda-item', 1, '2', 'core_catalog', '2', 'count',
        NULL, '1.00', '1', '1.00', '0.5'),
       ('order-id-2', 3, 'eda-item', 1, '3', 'core_catalog', '2', 'count',
        NULL, '1.00', '-1', '1.00', '0.5');

INSERT INTO eats_ordershistory.feedbacks(
    order_id, rating, comment
)
VALUES ('order-id-1', NULL, NULL),
       ('order-id-2', NULL, NULL);

INSERT INTO eats_ordershistory.addresses(
    order_id, full_address, entrance,
    floor_number, office, doorcode, comment
)
VALUES ('order-id-1', 'address1', '2', '4', '13', '34452', 'comment1'),
       ('order-id-2', 'address2', NULL, '4', '13', NULL, 'comment2');
