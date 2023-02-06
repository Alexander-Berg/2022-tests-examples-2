INSERT INTO catalog.depots
(depot_id, slug, geojson_zone, name, timezone, working_hours, currency, region_id) VALUES
(
	2,
   	'lavka_1',
   	'{"type": "MultiPolygon", "coordinates": [[[[37, 55], [37, 56], [38, 56], [38, 55], [37,55]]]]}'::JSONB,
   	'pretry lavka name',
   	'Europe/Moscow',
    INT4RANGE(900, 2000),
    'RUB',
    1
);

-- Test that always_show is cleared on import
INSERT INTO catalog.depot_category_settings
(depot_id, category_id, sort_order, always_show, updated) VALUES
(2, 'always_show_cleared', 0, true, NOW());
