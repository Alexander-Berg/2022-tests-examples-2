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
       (2002, 'tag2');

INSERT INTO state.entities (id, value, type)
VALUES
       (3000, 'user_phone_id_0', 'user_phone_id'),
       (3001, 'car_number_0', 'car_number'),
       (3002, 'udid_0', 'udid'),
       (3003, 'dbid_uuid_0', 'dbid_uuid'),
       (3004, 'park_car_id_0', 'park_car_id'),
       (3005, 'park_car_id_1', 'park_car_id'),
       (3006, 'park', 'park');


INSERT INTO state.tags (tag_name_id, provider_id, entity_id, updated, ttl, entity_type)
VALUES
       (2000, 1000, 3000, '2020-01-01 00:00:00', 'infinity', 'user_phone_id'),
       (2000, 1000, 3001, '2020-01-02 01:00:00', 'infinity', 'car_number'),
       (2001, 1001, 3001, '2020-01-03 02:00:00', 'infinity', 'car_number'),
       (2002, 1002, 3002, '2020-11-04 03:00:00', 'infinity', 'udid'),
       (2000, 1000, 3003, '2020-11-05 04:00:00', 'infinity', 'dbid_uuid'),
       (2000, 1000, 3004, '2020-11-06 05:00:00', 'infinity', 'park_car_id'),
       (2001, 1001, 3005, '2020-11-07 06:00:00', 'infinity', 'park_car_id'),
       (2002, 1002, 3006, '2020-11-08 07:00:00', 'infinity', 'park'),
       (2000, 1001, 3004, '2020-11-09 08:00:00', 'infinity', 'park_car_id'),
       (2000, 1000, 3005, '2020-11-08 09:00:00', 'infinity', 'park_car_id'),
       (2001, 1001, 3000, '2020-01-07 08:00:00', 'infinity', 'user_phone_id'),
       (2002, 1002, 3001, '2020-01-06 07:00:00', 'infinity', 'car_number');


