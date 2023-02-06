INSERT INTO invites.invites
    (id, exam, entity_type, expires, comment)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'dkk', 'driver', '2220-09-22 00:00:00', 'Комментарий 1'),
    ('22222222-2222-2222-2222-222222222222', 'dkk', 'driver', '2220-09-22 00:00:00', 'Комментарий 2');

INSERT INTO invites.filters
    (invite_id, key, value)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'car_number', 'car_number-1'),
    ('11111111-1111-1111-1111-111111111111', 'park_id', 'park-1'),
    ('22222222-2222-2222-2222-222222222222', 'car_number', 'car_number-2'),
    ('22222222-2222-2222-2222-222222222222', 'park_id', 'non_existent_park');
