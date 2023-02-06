INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, title, location, timezone, region_id, currency, status, source, extended_zones, phone_number, directions, telegram)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        '111',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_1',
        'Moscow lavka',
        (0, 0)::catalog_wms.depot_location,
        'Europe/Moscow',
        213,
        'RUB',
        'active'::catalog_wms.depot_status,
        '1C'::catalog_wms.depot_source,
        ARRAY[
            (
                'yandex-taxi',
                '{"type": "MultiPolygon", "coordinates": [[[[1, 1], [2, 2], [3, 3], [1, 1]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','20:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            ),
            (
               'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[1.5, 1.5], [2.5, 2.5], [3.5, 3.5]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','20:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            ),
            (
               'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[2, 2], [3, 3], [4.1, 4.1]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','20:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'disabled'
            )
      ]::catalog_wms.extended_zone_v1[],
        '+79091234455',
        'go to the right',
        'depot_telegram'
      );

INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, title, location, timezone, region_id, currency, status, source, extended_zones, phone_number, directions, telegram)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010001',
        '112',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_1',
        'Telaviv lavka',
        (14, 0)::catalog_wms.depot_location,
        'Europe/Moscow',
        131,
        'RUB',
        'active'::catalog_wms.depot_status,
        '1C'::catalog_wms.depot_source,
        ARRAY[
            (
                'yandex-taxi',
                '{"type": "MultiPolygon", "coordinates": [[[[11, 11], [12, 12], [13, 13], [11, 11]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            ),
            (
               'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[11.5, 11.5], [12.5, 12.5], [13.5, 13.5]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            ),
            (
               'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[12, 12], [13, 13], [14.1, 14.1]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'disabled'
            )
      ]::catalog_wms.extended_zone_v1[],
        '+79091234455',
        'go to the right',
        'depot_telegram'
      );


INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, title, location, timezone, region_id, currency, status, source, extended_zones, phone_number, directions, telegram, open_ts)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010003',
        '113',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_3',
        'Disabled Moscow lavka',
        (0, 0)::catalog_wms.depot_location,
        'Europe/Moscow',
        213,
        'RUB',
        'disabled'::catalog_wms.depot_status,
        '1C'::catalog_wms.depot_source,
        ARRAY[
            (
                'yandex-taxi',
                '{"type": "MultiPolygon", "coordinates": [[[[21, 21], [22, 22], [23, 23], [21, 21]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            ),
            (
               'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[21.5, 21.5], [22.5, 22.5], [23.5, 23.5]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            ),
            (
               'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[22, 22], [23, 23], [24.1, 24.1]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'disabled'
            )
      ]::catalog_wms.extended_zone_v1[],
        '+79091234455',
        'go to the right',
        'depot_telegram',
        '2019-12-01 01:01:01.000000+00'
      );
INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, title, location, timezone, region_id, currency, status, source, extended_zones, phone_number, directions, telegram, open_ts)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010004',
        '114',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_4',
        'Coming soon Moscow lavka',
        (0, 0)::catalog_wms.depot_location,
        'Europe/Moscow',
        213,
        'RUB',
        'disabled'::catalog_wms.depot_status,
        '1C'::catalog_wms.depot_source,
        ARRAY[
            (
                'yandex-taxi',
                '{"type": "MultiPolygon", "coordinates": [[[[31, 31], [32, 32], [33, 33], [31, 31]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            ),
            (
               'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[31.5, 31.5], [32.5, 32.5], [33.5, 33.5]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            ),
            (
               'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[32, 32], [33, 33], [34.1, 34.1]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'disabled'
            )
      ]::catalog_wms.extended_zone_v1[],
        '+79091234455',
        'go to the right',
        'depot_telegram',
        Null
      );

