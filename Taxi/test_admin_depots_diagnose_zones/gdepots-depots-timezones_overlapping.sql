INSERT INTO depots_wms.depots (source, updated, address, allow_parcels, currency, depot_id, directions, email, hidden,
                               external_id, location, name, phone_number, region_id, title, status, telegram, timezone)
VALUES ('WMS', current_timestamp, '', false, 'RUB', 'no-overlapping-depot', '', '', false, '99999903',
        (55.840757, 37.371618)::depots_wms.depot_location, 'test_lavka_1', '+78007700460', 213, '',
        'active'::depots_wms.depot_status, '', 'Europe/Moscow');
INSERT INTO depots_wms.depots (source, updated, address, allow_parcels, currency, depot_id, directions, email, hidden,
                               external_id, location, name, phone_number, region_id, title, status, telegram, timezone)
VALUES ('WMS', current_timestamp, '', false, 'RUB', 'different-timezones-depot', '', '', false, '99999904',
        (55.840757, 37.371618)::depots_wms.depot_location, 'test_lavka_1', '+78007700460', 213, '',
        'active'::depots_wms.depot_status, '', 'Europe/Moscow');
INSERT INTO depots_wms.depots (source, updated, address, allow_parcels, currency, depot_id, directions, email, hidden,
                               external_id, location, name, phone_number, region_id, title, status, telegram, timezone)
VALUES ('WMS', current_timestamp, '', false, 'RUB', 'timezones-overlapping-depot', '', '', false, '99999905',
        (55.840757, 37.371618)::depots_wms.depot_location, 'test_lavka_1', '+78007700460', 213, '',
        'active'::depots_wms.depot_status, '', 'Europe/Moscow');
