INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, title, location, timezone, region_id, currency, status, source, extended_zones, phone_number, directions, telegram)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        '111',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_1',
        'Мир Дошиков',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        'Europe/Moscow',
        213,
        'RUB',
        'active'::catalog_wms.depot_status,
        '1C'::catalog_wms.depot_source,
        '{}',
        '+79091234455',
        'go to the right',
        'depot_telegram'
      );
