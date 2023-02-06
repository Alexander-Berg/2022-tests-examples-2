INSERT INTO user_state.upgraded_class_orders ( 
  order_id, upgraded_to, yandex_uid, zone_name, brand, rating
)
VALUES
('test_order_id', 'some_class', 'test_yandex_uid', 'moscow', 'yataxibrand', NULL),
('test_order_id_2', 'some_class_2', 'test_yandex_uid', 'moscow', 'yataxibrand', NULL),
('test_order_id_3', 'some_class_3', 'test_yandex_uid', 'moscow', 'yataxibrand', NULL),
('bad_class_order_id', 'bad_class', 'test_yandex_uid', 'moscow', 'yataxibrand', NULL),
('rated_order_id', 'some_class', 'test_yandex_uid', 'moscow', 'yataxibrand', 5)
;

INSERT INTO user_state.upgraded_class_orders ( 
  order_id, upgraded_to, yandex_uid, zone_name, brand, rating, was_processed
)
VALUES
('processed_order_id', 'some_class', 'test_yandex_uid', 'moscow', 'yataxibrand', 1, true)
;
