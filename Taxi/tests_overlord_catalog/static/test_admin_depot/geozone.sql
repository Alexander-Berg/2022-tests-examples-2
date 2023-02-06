INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, title, location, extended_zones, timezone, region_id, currency, status, source)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        '111',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_1',
        'Мир Дошиков',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        ARRAY[
            (
                'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[11.1, 11.2], [11.3, 11.4],
                [11.5, 11.6]], [[12.1, 12.2], [12.3, 12.4], [12.5, 12.6]]], [[[21.1, 21.2],
                [21.3, 21.4], [21.5, 21.6]], [[22.1, 22.2], [22.3, 22.4], [22.5, 22.6]]]]}'::JSONB,
                ARRAY[('everyday'::catalog_wms.day_type, ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            )
        ]::catalog_wms.extended_zone_v1[],
        'Europe/Moscow',
        213,
        'RUB',
        'active'::catalog_wms.depot_status,
        '1C'::catalog_wms.depot_source);
