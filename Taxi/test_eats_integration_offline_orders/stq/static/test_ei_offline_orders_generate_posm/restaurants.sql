INSERT INTO restaurants (place_id, slug, name, pos_type, logo_link, description, enabled, tips_link_fallback, billing_client_id, geo_point, region_id, personal_tin_id, last_time_table_check)
VALUES
('place_id__1', 'place_id__1_slug', 'Самый тестовый ресторан', 'iiko', '135516/147734d81d1de576476c6a217679e1c29f83eeb7', 'Он настолько тестовый, что его можно только тестировать', TRUE, 'some_tips_link', 'billing_client_id__1', '(39.022872,45.056503)'::POINT, 13, 'personal_tin_id__1', '2022-05-16T10:00:00+00:00'),
('place_id__2', 'restaurant_slug_2', 'Ресторан "Мясо"', 'iiko', '', '', NULL, NULL, 'billing_client_id__2', NULL, NULL, 'personal_tin_id__2', '2022-05-16T10:00:00+00:00'),
('place_id__3', 'restaurant_slug_3', 'Ресторан "Компот"', 'iiko', '', '', FALSE, NULL, 'billing_client_id__3', NULL, NULL, 'personal_tin_id__3', '2022-05-16T10:00:00+00:00'),
('place_id__4', 'restaurant_slug_4', 'Кафе "У меня нет фантазии"', 'rkeeper', '', '', NULL, NULL, 'billing_client_id__4', NULL, NULL, 'personal_tin_id__4', '2022-05-16T10:00:00+00:00'),
('place_id__5', 'restaurant_slug_5', 'Ресторан "Hello, World!"', 'quick_resto', '', '', TRUE, NULL, 'billing_client_id__5', NULL, NULL, 'personal_tin_id__5', '2022-05-16T10:00:00+00:00')
;
