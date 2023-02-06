INSERT INTO eats_offers.offers (
    session_id, location, delivery_time, request_time,
    expiration_time, prolong_count, payload
)
VALUES ('session-id-1', ('1,1'), '2019-10-31T12:00:00Z', '2019-10-31T11:00:00Z',
        '2019-10-31T11:20:00Z', 1, '{"extra-data": "value"}'),
       ('session-id-2', ('2,2'), '2019-10-31T12:00:00Z', '2019-10-31T10:00:00Z',
        '2019-10-31T10:10:00Z', 2, '{"extra-data": "value"}'),
       ('session-id-3', ('3,3'), '2019-10-31T12:00:00Z', '2019-10-31T10:00:00Z',
        '2019-10-31T11:09:30Z', 10, '{"extra-data": "value"}'),
       ('session-id-4', ('4,4'), '2019-10-31T12:00:00Z', '2019-10-31T10:00:00Z',
        '2019-10-31T11:09:30Z', 5, '{"extra-data": "value"}'),
       ('session-id-5', ('5,5'), NULL, '2019-10-31T11:00:00Z',
        '2019-10-31T11:20:00Z', 5, '{"extra-data": "value"}'),
       ('session-id-6', ('6,6'), NULL, '2019-10-31T10:00:00Z',
        '2019-10-31T11:09:30Z', 6, '{"extra-data": "value"}'),
       ('session-id-7', ('4,4'), '2019-10-31T12:00:00Z', '2019-10-31T10:00:00Z',
        '2019-10-31T11:09:30Z', 5, '{"extra-data": "value"}'),
       ('session-id-8', ('4,4'), '2019-10-31T12:00:00Z', '2019-10-31T10:00:00Z',
        '2019-10-31T11:09:30Z', 5, '{"extra-data": "value"}'),

       -- bound sessions
       ('bound-session-id-9-2', ('4,4'), '2019-10-31T12:00:00Z', '2019-10-31T10:02:00Z',
        '2019-10-31T11:25:00Z', 1, '{"extra-data": "value"}'),
       ('session-id-9', ('4,4'), '2019-10-31T12:00:00Z', '2019-10-31T10:00:00Z',
        '2019-10-31T11:11:00Z', 1, '{"extra-data": "value"}'),
       ('bound-session-id-9', ('4,4'), '2019-10-31T12:00:00Z', '2019-10-31T10:01:00Z',
        '2019-10-31T11:15:00Z', 1, '{"extra-data": "value"}'),

       ('session-id-10', ('4,4'), '2019-10-31T12:00:00Z', '2019-10-31T10:10:00Z',
        '2019-10-31T11:25:00Z', 1, '{"extra-data": "value"}'),
       ('bound-session-id-10', ('4,4'), '2019-10-31T12:00:00Z', '2019-10-31T10:00:00Z',
        '2019-10-31T11:15:00Z', 1, '{"extra-data": "value"}')


ON CONFLICT DO NOTHING;


INSERT INTO eats_offers.offers (
    session_id, user_id, location, delivery_time, request_time,
    expiration_time, prolong_count, payload
)
VALUES ('session-id-11', 'user-id-1', ('1,1'), '2019-10-31T12:00:00Z', '2019-10-31T11:00:00Z',
        '2019-10-31T11:20:00Z', 0, '{"extra-data": "value"}'),
       ('session-id-12', 'user-id-1', ('1,1'), '2019-10-31T12:00:00Z', '2019-10-31T11:05:00Z',
        '2019-10-31T11:20:00Z', 0, '{"extra-data": "value"}'),
       ('session-id-13', 'user-id-1', ('1,1'), '2019-10-31T12:00:00Z', '2019-10-31T11:01:00Z',
        '2019-10-31T11:20:00Z', 0, '{"extra-data": "value"}'),
       ('session-id-14', 'user-id-1', ('2,2'), '2019-10-31T12:00:00Z', '2019-10-31T11:00:00Z',
        '2019-10-31T11:20:00Z', 0, '{"extra-data": "value"}'),
       ('session-id-15', 'user-id-2', ('3,3'), '2019-10-31T12:00:00Z', '2019-10-31T11:00:00Z',
        '2019-10-31T11:20:00Z', 0, '{"extra-data": "value 2"}'),
       ('session-id-16', 'user-id-3', ('1,1'), '2019-10-31T12:00:00Z', '2019-10-31T11:00:00Z',
        '2019-10-31T11:05:00Z', 0, '{"extra-data": "value 2"}'),
       ('session-id-17', 'user-id-4', ('1,1'), '2019-10-31T12:00:00Z', '2019-10-31T11:01:00Z',
        '2019-10-31T11:20:00Z', 0, '{"extra-data": "value 2"}'),
       ('session-id-18', 'user-id-4', ('1,1'), '2019-10-31T12:00:00Z', '2019-10-31T11:01:00Z',
        '2019-10-31T11:05:00Z', 0, '{"extra-data": "value 2"}'),
       ('session-id-19', 'p_user-id-2', ('3,3'), '2019-10-31T12:00:00Z', '2019-10-31T11:00:00Z',
        '2019-10-31T11:20:00Z', 0, '{"extra-data": "value 2"}')
ON CONFLICT DO NOTHING;

-- floor
INSERT INTO eats_offers.offers (
    session_id, user_id, location, delivery_time, request_time,
    expiration_time, prolong_count, payload
)
VALUES ('session-id-floor', 'user-id-1', ('4,4'), '2019-10-31T12:00:00Z', '2019-10-31T11:23:37Z',
        '2019-10-31T11:35:00Z', 0, '{"extra-data": "value"}')
ON CONFLICT DO NOTHING;
