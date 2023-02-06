INSERT INTO depots_wms.depots (source, updated, address, allow_parcels, assortment_id, currency, depot_id, directions,
                               email, hidden, external_id, location, name, phone_number, price_list_id, region_id,
                               root_category_id, title, status, telegram, timezone)
VALUES ('WMS', current_timestamp, '', false, '99999901ASTMNT', 'RUB', 'id-99999901', '', '', false, '99999901',
        (55.840757, 37.371618)::depots_wms.depot_location, 'test_lavka_1', '+78007700460', '99999901PRLIST', 213,
        'root-99999901', '"Партвешок За Полтишок" на Никольской', 'active'::depots_wms.depot_status, '',
        'Europe/Moscow');
