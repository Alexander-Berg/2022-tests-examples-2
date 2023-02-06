INSERT INTO catalog.depots
(depot_id, created, updated, slug, geojson_zone, name, timezone, working_hours, region_id, currency)
VALUES (1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'depot1', '{}', 'Depot One', 'Europe/Moscow', '[800,2300)', 123, 'RUB');

INSERT INTO catalog.depots
(depot_id, created, updated, slug, geojson_zone, name, timezone, working_hours, region_id, currency)
VALUES (2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'depot2', '{}', 'Depot Two', 'Europe/Moscow', '[800,2300)', 456, 'RUB');

INSERT INTO catalog.depots
(depot_id, created, updated, slug, geojson_zone, name, timezone, working_hours, region_id, currency)
VALUES (3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'depot3', '{}', 'Depot Three', 'Europe/Moscow', '[800,2300)', 789, 'RUB');

INSERT INTO catalog.categories
(category_id, parent, name, description, age_group, images, updated) VALUES
('cat1', 'parent', 'foo', 'foo', '', '{}', '2020-01-22 16:04:21.190977+03');
INSERT INTO catalog.categories
(category_id, parent, name, description, age_group, images, updated) VALUES
('cat2', 'parent', 'foo', 'foo', '', '{}', '2020-01-22 16:04:21.190977+03');

INSERT INTO catalog.goods (product_id, code, name, full_name, description, age_group, unit, quantity, images, updated) VALUES
('good1', '2578', 'Лента от мух «Раптор»', 'Лента липкая от мух «Раптор», 1 шт', 'Лента липкая от мух «Раптор» , 1шт. Срок хранения, дней: .', '', 'шт', 1.0000, '{}', '2020-01-22 16:09:41.85858+03');
INSERT INTO catalog.goods (product_id, code, name, full_name, description, age_group, unit, quantity, images, updated) VALUES
('good2', '2579', 'Лента от мух «Раптор»', 'Лента липкая от мух «Раптор», 1 шт', 'Лента липкая от мух «Раптор» , 1шт. Срок хранения, дней: .', '', 'шт', 1.0000, '{}', '2020-01-22 16:09:41.85858+03');

INSERT INTO catalog.depot_category_settings (depot_id, category_id, sort_order, always_show, updated) VALUES
(1, 'cat1', 0, true, '2020-01-22 16:20:49.914096+03');
INSERT INTO catalog.depot_category_settings (depot_id, category_id, sort_order, always_show, updated) VALUES
(2, 'cat1', 0, true, '2020-01-22 16:20:49.914096+03');
INSERT INTO catalog.depot_category_settings (depot_id, category_id, sort_order, always_show, updated) VALUES
(2, 'cat2', 0, true, '2020-01-22 16:20:49.914096+03');

INSERT INTO catalog.depot_goods_settings (depot_id, product_id, sort_order, always_show, price, currency, in_stock, updated) VALUES
(1, 'good1', 0, false, 170.0000, 'RUB', 1, '2020-01-22 16:21:26.24748+03');
INSERT INTO catalog.depot_goods_settings (depot_id, product_id, sort_order, always_show, price, currency, in_stock, updated) VALUES
(3, 'good1', 0, false, 170.0000, 'RUB', 1, '2020-01-22 16:21:26.24748+03');
INSERT INTO catalog.depot_goods_settings (depot_id, product_id, sort_order, always_show, price, currency, in_stock, updated) VALUES
(3, 'good2', 0, false, 170.0000, 'RUB', 1, '2020-01-22 16:21:26.24748+03');
