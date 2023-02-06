INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, location, extended_zones, timezone, region_id, currency, status, source, address, phone_number, company_id, title, oebs_depot_id)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        '2',
        '2019-12-01 01:01:01.000000+00',
        'lavka_1',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        ARRAY[
            (
                'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[37, 55], [37, 56], [38, 56], [38, 55], [37,55]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            )
        ]::catalog_wms.extended_zone_v1[],
        'Europe/Moscow',
        1,
        'RUB',
        'active'::catalog_wms.depot_status,
        'WMS'::catalog_wms.depot_source,
        '140015, Московская обл, Люберцы г, Инициативная ул, дом № 50',
        '8(999)7777777',
        'company-id-franchise',
        'Инициативная, 50',
        'oebs-depot-id-for-lavka_1');

INSERT INTO catalog_wms.depots
(depot_id, external_id, updated, name, location, extended_zones, timezone, region_id, currency, status, source, company_id)
VALUES ('aab8a6fbcee34b38b5281d8ea6ef749a000100010000',
        '3',
        '2019-12-01 01:01:01.000000+00',
        'lavka_2',
        (37.371618, 55.840757)::catalog_wms.depot_location,
        ARRAY[
            (
                'foot',
                '{"type": "MultiPolygon", "coordinates": [[[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]]}'::JSONB,
                ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
                'active'
            )
        ]::catalog_wms.extended_zone_v1[],
        'Europe/Moscow',
        1,
        'RUB',
        'active'::catalog_wms.depot_status,
        'WMS'::catalog_wms.depot_source,
        'company-id-yandex');


INSERT INTO catalog_wms.companies
(company_id, external_id, ownership, title, fullname, legal_address, actual_address, address, phone, email, psrn, tin, ies, okpo, okved, pay_account, cor_account, bic, bank_info)
VALUES ('company-id-yandex',
        'external-id',
        'yandex',
        'Yandex',
        'Общество с ограниченной ответственностью «До обновления»',
        'legal_address до обновления',
        'actual_address до обновления',
        'address до обновления',
        'телефон до обновления',
        'before@update.ru',
        '00000000',
        'tin-11111111',
        '2222222222',
        '3333333333',
        '44.44.4',
        '55555555555555555555',
        '66666666666666666666',
        '77777777',
        'АО «Банк до обновления»');


INSERT INTO catalog_wms.companies
(company_id, external_id, ownership, title, fullname, legal_address, actual_address, address, phone, email, psrn, tin, ies, okpo, okved, pay_account, cor_account, bic, bank_info)
VALUES ('company-id-franchise',
        'external-id',
        'franchisee',
        'Franchise',
        'Общество с ограниченной ответственностью «До обновления»',
        'legal_address до обновления',
        'actual_address до обновления',
        'address до обновления',
        'телефон до обновления',
        'before@update.ru',
        '00000000',
        'tin-for-franchise',
        '2222222222',
        '3333333333',
        '44.44.4',
        '55555555555555555555',
        '66666666666666666666',
        '77777777',
        'АО «Банк до обновления»');
