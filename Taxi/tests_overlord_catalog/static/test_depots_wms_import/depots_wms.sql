INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, location, zone, timezone, region_id, currency, status, source, company_id)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        '71249',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_1',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        '{"type": "MultiPolygon", "coordinates": [[[[37.371618, 55.840757], [37.371039, 55.839719], [37.37252, 55.837811]]]]}',
        'Europe/Moscow',
        213,
        'RUB',
        'active'::catalog_wms.depot_status,
        'WMS'::catalog_wms.depot_source,
        'yandex-lavka-id');

INSERT INTO catalog_wms.companies
(company_id, external_id, ownership, title, fullname, legal_address, actual_address, address, phone, email, psrn, tin, ies, okpo, okved, pay_account, cor_account, bic, bank_info)
VALUES ('not-yandex-lavka-id',
        'external-id-before-update',
        'franchisee',
        'ООО «До обновления»',
        'Общество с ограниченной ответственностью «До обновления»',
        'legal_address до обновления',
        'actual_address до обновления',
        'address до обновления',
        'телефон до обновления',
        'before@update.ru',
        '00000000',
        '11111111',
        '2222222222',
        '3333333333',
        '44.44.4',
        '55555555555555555555',
        '66666666666666666666',
        '77777777',
        'АО «Банк до обновления»');
