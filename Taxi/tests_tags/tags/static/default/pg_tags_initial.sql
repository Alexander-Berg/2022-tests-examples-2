INSERT INTO state.providers (id, name, description, active)
VALUES
       (1000, 'active_provider', 'always active', TRUE),
       (1001, 'disabled_provider', 'always disabled', FALSE),
       (1002, 'unstable_provider', 'initially active', TRUE);

INSERT INTO service.providers (provider_id, service_names)
VALUES
       (1000, '{"service0", "service1"}'),
       (1001, '{"service1"}'),
       (1002, '{"service2"}');

INSERT INTO meta.tag_names (id, name)
VALUES
       (2000, 'tag0'),
       (2001, 'tag1'),
       (2002, 'tag2'),
       (2003, 'tag3'),
       (2004, 'tag4'),
       (2005, 'tag5');

INSERT INTO state.entities (id, value, type)
VALUES
       (3000, 'LICENSE0', 'driver_license'),
       (3001, 'LICENSE1', 'driver_license'),        -- dbid1_uuid1
       (3002, 'LICENSE2', 'driver_license'),        -- dbid2_uuid2
       (3003, '000000000000000000000001', 'udid'),  -- dbid1_uuid1 dbid5_uuid5
       (3004, '000000000000000000000004', 'udid'),
       (3005, 'LICENSE2:1', 'driver_license'),
       (3006, 'А555АА555', 'car_number'),           -- dbid5_uuid5
       (3008, '+792155555', 'phone'),               -- dbid5_uuid5
       (3009, 'dbid1_uuid1', 'dbid_uuid'),          -- dbid1_uuid1
       (3010, 'dbid5_uuid5', 'dbid_uuid');          -- dbid5_uuid5

INSERT INTO
    state.tags (tag_name_id, provider_id, entity_id, updated, ttl, entity_type)
VALUES
       (2000, 1000, 3000, '1970-01-01 00:00:00', 'infinity', 'driver_license'),
       (2000, 1000, 3001, '1970-01-01 00:00:00', 'infinity', 'driver_license'),
       (2001, 1001, 3001, '1970-01-01 00:00:00', 'infinity', 'driver_license'),
       (2001, 1001, 3003, '1970-01-01 00:00:00', 'infinity', 'udid'),
       (2002, 1002, 3002, '1970-01-01 00:00:00', 'infinity', 'udid'),
       (2002, 1000, 3003, '1970-01-01 00:00:00', '1980-01-01 00:00:00', 'udid'),
       (2001, 1000, 3003, '1980-01-01 00:00:00', '2040-01-01 00:00:00', 'udid'),
       (2001, 1000, 3006, '1980-01-01 00:00:00', '2041-01-01 01:01:01', 'car_number'),
       (2000, 1000, 3005, '1970-01-01 00:00:00', 'infinity', 'driver_license'),
       (2002, 1000, 3004, '1970-01-01 00:00:00', 'infinity', 'udid'),
       (2003, 1000, 3006, '1970-01-01 00:00:00', 'infinity', 'car_number'),
       (2003, 1000, 3009, '1970-01-01 00:00:00', 'infinity', 'dbid_uuid'),
       (2005, 1000, 3010, '1970-01-01 00:00:00', '2020-02-02 02:02:02', 'dbid_uuid');
