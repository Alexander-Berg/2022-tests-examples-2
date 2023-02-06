INSERT INTO catalog.depots
(depot_id, created, updated, slug, geojson_zone, name, timezone, working_hours, region_id, currency)
VALUES (1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'test_lavka_1', '{"type": "MultiPolygon", "coordinates": [[[[1, 1], [2, 2], [3, 3]]]]}', 'Мир Дошиков', 'Europe/Moscow', '[800,2300)', 213, 'RUB');

INSERT INTO catalog.depots
(depot_id, created, updated, slug, geojson_zone, name, timezone, working_hours, region_id, currency)
VALUES (2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'test_lavka_2', '{"type": "MultiPolygon", "coordinates": [[[[1, 1], [2, 2], [3, 3]]]]}', 'Мир Дошиков', 'Europe/Moscow', '[800,2300)', 213, 'RUB');

INSERT INTO catalog.depots
(depot_id, created, updated, slug, geojson_zone, name, timezone, working_hours, region_id, currency)
VALUES (3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'test_lavka_3', '{"type": "MultiPolygon", "coordinates": [[[[1, 1], [2, 2], [3, 3]]]]}', 'Мир Дошиков', 'Europe/Moscow', '[800,2300)', 213, 'RUB');
