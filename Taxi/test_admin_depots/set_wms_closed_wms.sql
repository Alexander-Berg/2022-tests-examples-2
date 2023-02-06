INSERT INTO depots_wms.depots
(depot_id, external_id, updated, name, location, timezone, region_id, currency, status, source, timetable, open_ts, hidden)
VALUES ('id-333',
        '333',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_3',
        (37.371618, 55.840757)::depots_wms.depot_location,
        'Europe/Moscow',
        213,
        'RUB',
        'closed'::depots_wms.depot_status,
        '1C'::depots_wms.depot_source,
        ARRAY[('everyday'::depots_wms.day_type, ('08:00','23:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        '2021-08-23 07:09:31.000000 +00:00',
        FALSE);
