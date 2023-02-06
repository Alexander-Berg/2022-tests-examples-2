INSERT INTO invites.invites
    (id, exam, entity_type, expires, comment, status, identity, identity_type)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'dkk', 'driver', '2220-09-22 00:00:00', 'Комментарий 1', 'prepared',
     'jora', 'assessor');

INSERT INTO invites.filters
    (invite_id, key, value)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'car_number', 'car_number-1');

INSERT INTO invites.entities
    (invite_id, entity_id, entity_type)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'park_id_driver_id_1', 'driver'),
    ('11111111-1111-1111-1111-111111111111', 'park_id_driver_id_2', 'driver'),
    ('11111111-1111-1111-1111-111111111111', 'park_id_driver_id_3', 'driver'),
    ('11111111-1111-1111-1111-111111111111', 'park_id_driver_id_4', 'driver'),
    ('11111111-1111-1111-1111-111111111111', 'park_id_driver_id_5', 'driver');
