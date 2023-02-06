INSERT INTO blocklist.predicates
    (id,
     value,
     kwarg_keys,
     indexible_kwargs,
     designation)
VALUES
    ('11111111-1111-1111-1111-111111111111',
     '{"type":"eq","value":"car_number"}',
     ARRAY['car_number'], ARRAY['car_number'],
     'car_number'
     ),
    ('22222222-2222-2222-2222-222222222222',
     '{"type":"and","value":[{"type":"eq","value":"park_id"},{"type":"eq","value":"car_number"}]}',
     ARRAY['park_id', 'car_number'], ARRAY['car_number'],
     'park_car_number'
     ),
    ('33333333-3333-3333-3333-333333333333',
     '{"type":"eq","value":"license_id"}',
     ARRAY['license_id'], ARRAY['license_id'],
     'license_id'
     ),
    ('44444444-4444-4444-4444-444444444444',
     '{"type":"and","value":[{"type":"eq","value":"park_id"},{"type":"eq","value":"license_id"}]}',
     ARRAY['park_id', 'license_id'], ARRAY['license_id'],
     'park_license_id'
     );


INSERT INTO blocklist.cursors
(name, value)
VALUES
    ('communication-sender-drivers', 0),
    ('communication-sender-parks', 0);
