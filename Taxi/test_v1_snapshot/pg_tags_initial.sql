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

INSERT INTO meta.topics (id, name, description)
VALUES
       (4000, 'topic0', 'topic0_description'),
       (4001, 'topic1', 'topic1_description'),
       (4002, 'topic2', 'topic2_description');

INSERT INTO state.entities (id, value, type)
VALUES
       (3000, 'PARK_CAR0', 'park_car_id'),
       (3001, 'PARK_CAR1', 'park_car_id'),
       (3002, 'PARK_CAR2', 'park_car_id'),
       (3003, 'udid3', 'udid'),
       (3004, 'udid4', 'udid');

INSERT INTO meta.relations (topic_id, tag_name_id)
VALUES
       (4000, 2000),
       (4001, 2000),
       (4001, 2002);

INSERT INTO state.tags (tag_name_id, provider_id, entity_id, updated, ttl, entity_type)
VALUES
       (2000, 1000, 3000, '1970-01-01 00:00:00', 'infinity', 'park_car_id'),
       (2000, 1000, 3001, '1970-01-01 00:00:00', 'infinity', 'park_car_id'),
       (2001, 1001, 3001, '1970-01-01 00:00:00', 'infinity', 'park_car_id'),
       (2002, 1002, 3002, '1970-01-01 00:00:00', 'infinity', 'park_car_id');
