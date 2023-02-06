INSERT INTO eats_ordershistory.orders(
    order_id, order_source, eats_user_id, taxi_user_id, yandex_uid,
    place_id, status, delivery_location, total_amount, is_asap,
    cancel_reason, created_at, delivered_at
)
VALUES
-- user 1
       ('order-id-1', 'eda', 1, NULL, NULL, 123, 'finished', '(1,1)',
        '123.45', True, NULL, '2019-10-31T12:01:00Z', NULL),
       ('order-id-2', 'eda', 1, NULL, NULL, 123, 'finished', '(1,1)',
        '123.45', True, NULL, '2019-10-31T12:02:00Z', NULL),
       ('order-id-3', 'eda', 1, NULL, NULL, 123, 'finished', '(1,1)',
        '123.45', True, NULL, '2019-10-31T12:03:00Z', NULL),
       ('order-id-4', 'eda', 1, NULL, NULL, 123, 'finished', '(1,1)',
        '123.45', True, NULL, '2019-10-31T12:04:00Z', NULL),
       ('order-id-5', 'eda', 1, NULL, NULL, 123, 'finished', '(1,1)',
        '123.45', True, NULL, '2019-10-31T12:05:00Z', NULL),
       ('order-id-6', 'eda', 1, NULL, NULL, 123, 'finished', '(1,1)',
        '123.45', True, NULL, '2019-10-31T12:06:00Z', NULL),
       ('order-id-7', 'eda', 1, NULL, NULL, 123, 'finished', '(1,1)',
        '123.45', True, NULL, '2019-10-31T12:07:00Z', NULL),
-- user 2
       ('order-id-8', 'eda', 2, NULL, NULL, 123, 'finished', '(1,1)',
        '123.45', True, NULL, '2019-10-31T12:08:00Z', NULL),
       ('order-id-9', 'eda', 2, NULL, NULL, 123, 'finished', '(1,1)',
        '123.45', True, NULL, '2019-10-31T12:09:00Z', NULL),
       ('order-id-10', 'eda', 2, NULL, NULL, 123, 'finished', '(1,1)',
        '123.45', True, NULL, '2019-10-31T12:10:00Z', NULL)
ON CONFLICT (order_id) DO NOTHING;

INSERT INTO eats_ordershistory.cart_items(
    order_id, place_menu_item_id, name, quantity, origin_id, catalog_type
)
VALUES
-- user 1
       ('order-id-1', 1, 'eda-item', 1, '1', 'core_catalog'),
       ('order-id-1', 2, 'eda-item', 1, '2', 'core_catalog'),
       ('order-id-1', 3, 'eda-item', 1, '3', 'core_catalog'),
       ('order-id-2', 1, 'eda-item', 1, '1', 'core_catalog'),
       ('order-id-2', 2, 'eda-item', 1, '2', 'core_catalog'),
       ('order-id-2', 3, 'eda-item', 1, '3', 'core_catalog'),
       ('order-id-3', 1, 'eda-item', 1, '1', 'core_catalog'),
       ('order-id-3', 2, 'eda-item', 1, '2', 'core_catalog'),
       ('order-id-3', 3, 'eda-item', 1, '3', 'core_catalog'),
-- user 2
       ('order-id-8', 1, 'eda-item', 1, '1', 'core_catalog'),
       ('order-id-8', 2, 'eda-item', 1, '2', 'core_catalog'),
       ('order-id-8', 3, 'eda-item', 1, '3', 'core_catalog')
ON CONFLICT (order_id, catalog_type, origin_id) DO NOTHING;

INSERT INTO eats_ordershistory.feedbacks(
    order_id, rating, comment
)
VALUES
-- user 1
       ('order-id-1', NULL, NULL),
       ('order-id-2', NULL, NULL),
       ('order-id-3', NULL, NULL),
       ('order-id-4', NULL, NULL),
       ('order-id-5', NULL, NULL),
       ('order-id-6', NULL, NULL),
       ('order-id-7', NULL, NULL),
-- user 2
       ('order-id-8', NULL, NULL),
       ('order-id-9', NULL, NULL),
       ('order-id-10', NULL, NULL)
ON CONFLICT (order_id) DO NOTHING;

INSERT INTO eats_ordershistory.addresses(
    order_id, full_address, entrance,
    floor_number, office, doorcode, comment
)
VALUES
-- user 1
       ('order-id-1', 'address1', '2', '4', '13', '34452', 'comment1'),
       ('order-id-2', 'address2', NULL, '4', '13', NULL, 'comment2'),
       ('order-id-3', 'address3', NULL, NULL, NULL, NULL, NULL),
       ('order-id-4', 'address4', '56', NULL, '19', '45', NULL),
       ('order-id-5', NULL, NULL, NULL, NULL, NULL, NULL),
       ('order-id-6', 'address5', '83', '12', '13', '1332', 'comment5'),
       ('order-id-7', 'address6', NULL, NULL, NULL, NULL, 'comment6'),
-- user 2
       ('order-id-8', 'address7', '29', '43', '83', '12', 'comment7'),
       ('order-id-9', NULL, NULL, NULL, NULL, NULL, 'comment8'),
       ('order-id-10', 'address9', '3429', '4', '483', '122', 'comment9')
ON CONFLICT (order_id) DO NOTHING;
