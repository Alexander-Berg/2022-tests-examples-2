INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, location, zone, timezone, region_id, currency, status, source, timetable, hidden)
VALUES ('id-111',
        '111',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_1',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        '{"type": "MultiPolygon", "coordinates": [[[[37.371618, 55.840757], [37.371039, 55.839719], [37.37252, 55.837811]]]]}',
        'Europe/Moscow',
        213,
        'RUB',
        'disabled'::catalog_wms.depot_status,
        '1C'::catalog_wms.depot_source,
        ARRAY[('everyday'::catalog_wms.day_type, ('08:00','23:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
        FALSE);

INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, location, zone, timezone, region_id, currency, status, source, timetable, hidden)
VALUES ('id-222',
        '222',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_2',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        '{"type": "MultiPolygon", "coordinates": [[[[37.371618, 55.840757], [37.371039, 55.839719], [37.37252, 55.837811]]]]}',
        'Europe/Moscow',
        213,
        'RUB',
        'active'::catalog_wms.depot_status,
        '1C'::catalog_wms.depot_source,
        ARRAY[('everyday'::catalog_wms.day_type, ('08:00','23:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
        TRUE);

INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, location, zone, timezone, region_id, currency, status, source, timetable, hidden)
VALUES ('id-333',
        '333',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_3',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        '{"type": "MultiPolygon", "coordinates": [[[[37.371618, 55.840757], [37.371039, 55.839719], [37.37252, 55.837811]]]]}',
        'Europe/Moscow',
        213,
        'RUB',
        'active'::catalog_wms.depot_status,
        '1C'::catalog_wms.depot_source,
        ARRAY[('everyday'::catalog_wms.day_type, ('08:00','23:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
        TRUE);
