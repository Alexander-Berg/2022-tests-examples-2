INSERT INTO depots_wms.depots (source, updated, depot_id, external_id, region_id, timezone, location, phone_number,
                               currency, status, hidden, title, name, price_list_id, root_category_id, assortment_id)
VALUES ('WMS', current_timestamp, 'id-99999901', '99999901', 213, 'Europe/Moscow',
        (37.371618, 55.840757)::depots_wms.depot_location, '', 'RUB', 'active'::depots_wms.depot_status, false,
        '"Партвешок За Полтишок" на Никольской', 'test_lavka_1', '99999901PRLIST', 'root-99999901', '99999901ASTMNT');
