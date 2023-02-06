INSERT INTO catalog.depots
(depot_id, slug, region_id, currency, enabled, hidden, updated, timezone, geojson_zone)
VALUES (111, 'test_lavka_1', 213, 'RUB', FALSE, FALSE, '2019-12-01 01:01:01.000000+00', 'Europe/Moscow', '{"type": "MultiPolygon", "coordinates": [[[[37.371618, 55.840757], [37.362992, 55.838922], [37.371618, 55.840757]]]]}');

INSERT INTO catalog.depots
(depot_id, slug, region_id, currency, enabled, hidden, updated, timezone, geojson_zone)
VALUES (222, 'test_lavka_2', 213, 'RUB', TRUE, TRUE, '2019-12-01 01:01:01.000000+00', 'Europe/Moscow', '{"type": "MultiPolygon", "coordinates": [[[[37.371618, 55.840757], [37.362992, 55.838922], [37.371618, 55.840757]]]]}');

INSERT INTO catalog.depots
(depot_id, slug, region_id, currency, enabled, hidden, updated, timezone, geojson_zone)
VALUES (333, 'test_lavka_3', 213, 'RUB', TRUE, TRUE, '2019-12-01 01:01:01.000000+00', 'Europe/Moscow', '{"type": "MultiPolygon", "coordinates": [[[[37.371618, 55.840757], [37.362992, 55.838922], [37.371618, 55.840757]]]]}');
