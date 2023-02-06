-- zones and markers are here https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
-- foot zone 1 is available 07:00-20:00 until test time + 1 day
-- foot zone 2 is bigger and  is available 07:00-20:00 after test time + 1 day
INSERT INTO depots_wms.depots
(depot_id, external_id, updated, name, address, title, location, timezone, region_id, currency, status, source)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        '111',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_1',
        'Доширбург, Яичное лапшассе, 39',
        'Мир Дошиков',
        (5.0, 5.0)::depots_wms.depot_location,
        'Europe/Moscow',
        213,
        'RUB',
        'active',
        'WMS'),
        ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010112',
        '112',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_1',
        'Доширбург, Яичное лапшассе, 39',
        'Мир Дошиков',
        (5.0, 5.0)::depots_wms.depot_location,
        'Europe/Moscow',
        213,
        'RUB',
        'active',
        'WMS'),
       ('soon_depot_id',
        '113',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_1',
        'Доширбург, Яичное лапшассе, 39',
        'Мир Дошиков',
        (5.0, 5.0)::depots_wms.depot_location,
        'Europe/Moscow',
        213,
        'RUB',
        'disabled',
        'WMS');

INSERT INTO depots_wms.zones
(zone_id, depot_id, status, created, updated, delivery_type, timetable, zone, effective_from, effective_till)
VALUES
    (
        'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000_foot_old',
        'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        'active',
        current_timestamp - '1 year'::interval,
        current_timestamp,
        'foot',
        ARRAY[('everyday', ('07:00','20:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        '{"type": "MultiPolygon", "coordinates": [[[[0.1, 0.0],[0.1, 0.1],[0.2, 0.1],[0.2, 0.0],[0.1, 0.0]]]]}'::JSONB,
        current_timestamp - '1 year'::interval,
        current_timestamp + '1 day'::interval
    ),
    (
        'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000_foot_new',
        'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        'active',
        current_timestamp - '1 year'::interval,
        current_timestamp,
        'foot',
        ARRAY[('everyday', ('07:00','20:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        '{"type": "MultiPolygon", "coordinates": [[[[0.2, 0.1],[0.3, 0.2],[0.3, 0.1],[0.2, 0.1]]]]}'::JSONB,
        current_timestamp + '1 day'::interval,
        NULL
    ),
    (
        'zone_id_112',
        'ddb8a6fbcee34b38b5281d8ea6ef749a000100010112',
        'active',
        current_timestamp - '1 year'::interval,
        current_timestamp,
        'yandex-taxi-remote',
        ARRAY[('everyday', ('07:00','23:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        '{"type": "MultiPolygon", "coordinates": [[[[0.15, 0.0],[0.3, 0.2],[0.3, 0.1],[0.15, 0.0]]]]}'::JSONB,
        current_timestamp - '1 year'::interval,
        current_timestamp + '1 day'::interval
    ),
    (
        'soon_zone_1',
        'soon_depot_id',
        'active',
        current_timestamp - '1 year'::interval,
        current_timestamp,
        'foot',
        ARRAY[('everyday', ('07:00','20:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        '{"type": "MultiPolygon", "coordinates": [[[[0.1, 0.0],[0.1, 0.1],[0.2, 0.1],[0.2, 0.0],[0.1, 0.0]]]]}'::JSONB,
        current_timestamp - '1 year'::interval,
        current_timestamp + '1 day'::interval
    ),
    (
        'soon_zone_2',
        'soon_depot_id',
        'active',
        current_timestamp - '1 year'::interval,
        current_timestamp,
        'foot',
        ARRAY[('everyday', ('07:00','20:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        '{"type": "MultiPolygon", "coordinates": [[[[0.2, 0.1],[0.3, 0.2],[0.3, 0.1],[0.2, 0.1]]]]}'::JSONB,
        current_timestamp + '1 day'::interval,
        NULL
    ),
    (
        'soon_zone_3',
        'soon_depot_id',
        'active',
        current_timestamp - '1 year'::interval,
        current_timestamp,
        'yandex-taxi-remote',
        ARRAY[('everyday', ('07:00','23:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        '{"type": "MultiPolygon", "coordinates": [[[[0.15, 0.0],[0.3, 0.2],[0.3, 0.1],[0.15, 0.0]]]]}'::JSONB,
        current_timestamp - '1 year'::interval,
        current_timestamp + '1 day'::interval
    );

