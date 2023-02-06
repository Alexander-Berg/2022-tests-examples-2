BEGIN TRANSACTION;

INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, title, location, extended_zones, timezone, region_id, currency, status, source)
VALUES ('id-99999901',
        '99999901',
        CURRENT_TIMESTAMP,
        'test_lavka_1',
        '"Партвешок За Полтишок" на Никольской',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        ARRAY[
            (
                'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[1, 2], [3, 4], [5, 6]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            )
        ]::catalog_wms.extended_zone_v1[],
        'Europe/Moscow',
        55501,
        'RUB',
        'active',
        '1C');

INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, title, location, extended_zones, timezone, region_id, currency, status, source)
VALUES ('id-99999902',
        '99999902',
        CURRENT_TIMESTAMP,
        'test_lavka_2',
        '"Партвешок За Полтишок" на Скоробогадько 17',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        ARRAY[
            (
                'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[1, 2], [3, 4], [5, 6]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            )
        ]::catalog_wms.extended_zone_v1[],
        'Europe/Moscow',
        55501,
        'RUB',
        'active',
        '1C');

INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, title, location, extended_zones, timezone, region_id, currency, status, source)
VALUES ('id-99999903',
        '99999903',
        CURRENT_TIMESTAMP,
        'test_lavka_3',
        '"Партвешок За Полтишок" на Внутреутробной',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        ARRAY[
            (
                'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[1, 2], [3, 4], [5, 6]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            )
        ]::catalog_wms.extended_zone_v1[],
        'Europe/Moscow',
        55502,
        'RUB',
        'active',
        '1C');

INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, title, location, extended_zones, timezone, region_id, currency, status, source)
VALUES ('id-99999904',
        '99999904',
        CURRENT_TIMESTAMP,
        'test_lavka_4',
        '"Партвешок За Полтишок" на Седьмой-Восьмой 9',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        ARRAY[
            (
                'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[1, 2], [3, 4], [5, 6]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            )
        ]::catalog_wms.extended_zone_v1[],
        'Europe/Moscow',
        55502,
        'RUB',
        'active',
        '1C');

INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, title, location, extended_zones, timezone, region_id, currency, status, source)
VALUES ('id-5',
        '5',
        CURRENT_TIMESTAMP,
        'mixed_lavka_6',
        '"Партвешок За Полтишок" на Большой Пятой',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        ARRAY[
            (
                'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[1, 2], [3, 4], [5, 6]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            )
        ]::catalog_wms.extended_zone_v1[],
        'Europe/Moscow',
        5,
        'RUB',
        'active',
        '1C');

INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, title, location, extended_zones, timezone, region_id, currency, status, source)
VALUES ('id-6',
        '6',
        CURRENT_TIMESTAMP,
        'mixed_lavka_5',
        '"Партвешок За Полтишок" на Малой Шестой',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        ARRAY[
            (
                'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[1, 2], [3, 4], [5, 6]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            )
        ]::catalog_wms.extended_zone_v1[],
        'Europe/Moscow',
        6,
        'RUB',
        'active',
        '1C');

INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, title, location, extended_zones, timezone, region_id, currency, status, source)
VALUES ('id-666666',
        '666666',
        CURRENT_TIMESTAMP,
        'perfect_for_trim',
        '"Партвешок За Полтишок" на Трима Обрезалова',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        ARRAY[
            (
                'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[1, 2], [3, 4], [5, 6]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            )
        ]::catalog_wms.extended_zone_v1[],
        'Europe/Moscow',
        66600,
        'RUB',
        'active',
        '1C');

INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, title, location, extended_zones, timezone, region_id, currency, status, source)
VALUES ('id-777777',
        '777777',
        CURRENT_TIMESTAMP,
        'so_damn_geo_zoned',
        '"Партвешок За Полтишок" на Крупица-Щепоткиной',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        ARRAY[
            (
                'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[11.1, 11.2], [11.3, 11.4], [11.5, 11.6]], [[12.1, 12.2], [12.3, 12.4], [12.5, 12.6]]], [[[21.1, 21.2], [21.3, 21.4], [21.5, 21.6]], [[22.1, 22.2], [22.3, 22.4], [22.5, 22.6]]]]}',
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            )
        ]::catalog_wms.extended_zone_v1[],
        'Europe/Moscow',
        77700,
        'RUB',
        'active',
        '1C');

COMMIT TRANSACTION;
