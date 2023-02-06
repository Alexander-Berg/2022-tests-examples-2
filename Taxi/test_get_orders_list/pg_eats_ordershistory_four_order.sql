INSERT INTO eats_ordershistory.orders (
    order_id, order_source, eats_user_id, taxi_user_id, yandex_uid,
    place_id, status, delivery_location, total_amount, is_asap,
    cancel_reason, created_at, delivered_at
) VALUES ('order-id-1', 'eda', 1, NULL, NULL, 123, 'delivered', '(1,1)',
          '123.45', True, NULL, '2021-07-20T12:01:00Z', NULL),
         ('order-id-2', 'eda', 1, NULL, NULL, 456, 'cancelled', '(1,1)',
          '123.45', True, NULL, '2021-07-25T12:01:00Z', NULL),
         ('order-id-3', 'eda', 1, NULL, NULL, 123, 'finished', '(1,1)',
          '123.45', True, NULL, '2021-07-29T12:01:00Z', NULL),
         ('order-id-4', 'eda', 1, NULL, NULL, 456, 'finished', '(1,1)',
          '123.45', True, NULL, '2021-07-29T12:01:00Z', NULL);

INSERT INTO eats_ordershistory.cart_items(
    order_id, place_menu_item_id, name, quantity, origin_id, catalog_type
)
VALUES ('order-id-1', 1, 'eda-item', 1, '1', 'core_catalog'),
       ('order-id-1', 2, 'eda-item', 1, '2', 'core_catalog'),
       ('order-id-1', 3, 'eda-item', 1, '3', 'core_catalog'),
       ('order-id-2', 1, 'eda-item', 1, '1', 'core_catalog'),
       ('order-id-2', 2, 'eda-item', 1, '2', 'core_catalog'),
       ('order-id-2', 3, 'eda-item', 1, '3', 'core_catalog'),
       ('order-id-3', 1, 'eda-item', 1, '1', 'core_catalog'),
       ('order-id-3', 2, 'eda-item', 1, '2', 'core_catalog'),
       ('order-id-3', 3, 'eda-item', 1, '3', 'core_catalog'),
       ('order-id-4', 1, 'eda-item', 1, '1', 'core_catalog'),
       ('order-id-4', 2, 'eda-item', 1, '2', 'core_catalog'),
       ('order-id-4', 3, 'eda-item', 1, '3', 'core_catalog');

INSERT INTO eats_ordershistory.feedbacks(
    order_id, rating, comment
)
VALUES ('order-id-1', NULL, NULL),
       ('order-id-2', NULL, NULL),
       ('order-id-3', NULL, NULL),
       ('order-id-4', NULL, NULL);

INSERT INTO eats_ordershistory.addresses(
    order_id, full_address, entrance,
    floor_number, office, doorcode, comment
)
VALUES ('order-id-1', 'address1', '2', '4', '13', '34452', 'comment1'),
       ('order-id-2', 'address2', NULL, '4', '13', NULL, 'comment2'),
       ('order-id-3', 'address3', NULL, NULL, NULL, NULL, NULL),
       ('order-id-4', 'address4', '56', NULL, '19', '45', NULL);
