INSERT INTO depots_wms.depots
(depot_id, external_id, updated, name, location, zone, timezone, region_id, currency, status, source, company_id)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        '71249',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_1',
        (37.371618, 55.840757)::depots_wms.depot_location,
        '{"type": "MultiPolygon", "coordinates": [[[[37.371618, 55.840757], [37.371039, 55.839719], [37.37252, 55.837811]]]]}',
        'Europe/Moscow',
        213,
        'RUB',
        'active'::depots_wms.depot_status,
        'WMS'::depots_wms.depot_source,
        'yandex-lavka-id');
