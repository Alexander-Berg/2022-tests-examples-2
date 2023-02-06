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
        '{"type": "MultiPolygon", "coordinates": [[[[37.64216423034668,55.73387629706783],[37.64343023300171,55.734552853773316],[37.64182090759277,55.73770593659091],[37.64008283615112,55.73701735403676],[37.64216423034668,55.73387629706783]]]]}'::JSONB,
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
        '{"type": "MultiPolygon", "coordinates": [[[[37.64216423034668,55.73386421559154],[37.64572620391845,55.73615962895247],[37.64167070388794,55.743153766729286],[37.63817310333252,55.74206667732932],[37.640061378479004,55.73699319302477],[37.64216423034668,55.73386421559154]]]]}'::JSONB,
        current_timestamp + '1 day'::interval,
        NULL
    ),
    (
        'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000_remote',
        'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        'active',
        current_timestamp - '1 year'::interval,
        current_timestamp,
        'yandex-taxi-remote',
        ARRAY[('everyday', ('07:00','23:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        '{"type": "MultiPolygon", "coordinates": [[[[37.64817237854004,55.73788714050709],[37.65426635742187,55.74296050860488],[37.65546798706055,55.74979643282958],[37.64066219329834,55.7473568941391],[37.64817237854004,55.73788714050709]]]]}'::JSONB,
        current_timestamp - '1 year'::interval,
        current_timestamp + '1 day'::interval
    ),
    (
        'standalone_zone_id',
        'no_such_depots_id',
        'active',
        current_timestamp - '1 year'::interval,
        current_timestamp,
        'yandex-taxi-remote',
        ARRAY[('everyday', ('07:00','23:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        '{"type": "MultiPolygon", "coordinates": [[[[37.64817237854004,55.73788714050709],[37.65426635742187,55.74296050860488],[37.65546798706055,55.74979643282958],[37.64066219329834,55.7473568941391],[37.64817237854004,55.73788714050709]]]]}'::JSONB,
        current_timestamp - '1 year'::interval,
        current_timestamp + '1 day'::interval
    );

