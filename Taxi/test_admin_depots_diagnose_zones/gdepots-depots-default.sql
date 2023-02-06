INSERT INTO depots_wms.depots (source, updated, address, allow_parcels, currency, depot_id, directions, email, hidden,
                               external_id, location, name, phone_number, region_id, title, status, telegram, timezone)
VALUES ('WMS', current_timestamp, '', false, 'RUB', 'id-99999901', '', '', false, '99999901',
        (55.840757, 37.371618)::depots_wms.depot_location, 'test_lavka_1', '+78007700460', 213,
        '"Партвешок За Полтишок" на Никольской', 'active'::depots_wms.depot_status, '', 'Europe/Moscow');
INSERT INTO depots_wms.depots (source, updated, address, allow_parcels, currency, depot_id, directions, email, hidden,
                               external_id, location, name, phone_number, region_id, title, status, telegram, timezone)
VALUES ('WMS', current_timestamp, '', false, 'RUB', 'id-99999902', '', '', false, '99999902',
        (55.840757, 37.371618)::depots_wms.depot_location, 'test_lavka_2', '+78007700460', 213,
        '"Партвешок За Полтишок" на Скоробогадько 17', 'active'::depots_wms.depot_status, '', 'Europe/Moscow');
INSERT INTO depots_wms.depots (source, updated, address, allow_parcels, currency, depot_id, directions, email, hidden,
                               external_id, location, name, phone_number, region_id, title, status, telegram, timezone)
VALUES ('WMS', current_timestamp, '', false, 'RUB', 'id-99999907', '', '', false, '99999907',
        (55.840757, 37.371618)::depots_wms.depot_location, 'test_lavka_7', '+78007700460', 213,
        '"Партвешок За Полтишок" на Скоробогадько 17', 'active'::depots_wms.depot_status, '', 'Europe/Moscow');
