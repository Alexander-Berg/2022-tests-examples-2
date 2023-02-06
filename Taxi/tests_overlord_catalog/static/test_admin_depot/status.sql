INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, location, extended_zones, timezone, region_id, currency, status, source, hidden)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        '111',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_1',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        ARRAY[
            (
                'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[1, 1], [2, 2], [3, 3]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            )
        ]::catalog_wms.extended_zone_v1[],
        'Europe/Moscow',
        213,
        'RUB',
        'active',
        '1C',
        TRUE),
       ('aab8a6fbcee34b38b5281d8ea6ef749a000100010000',
        '222',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_2',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        ARRAY[
            (
                'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[1, 1], [2, 2], [3, 3]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            )
        ]::catalog_wms.extended_zone_v1[],
        'Europe/Moscow',
        213,
        'RUB',
        'disabled',
        '1C',
        FALSE);
