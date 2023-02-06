INSERT INTO users
    (id, guid, first_name, last_name, msisdn, avatar, language_id)
VALUES
    (1, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'first_name', 'last_name', 'msisdn', 'avatar', 1),
    (2, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C', 'first_name', 'last_name', 'msisdn', 'avatar', 1),
    (4, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D', 'first_name', 'last_name', 'msisdn', 'avatar', 1);


INSERT INTO push_notification_tokens
    (id, user_guid, language_id, token, hash, device_type, application_id, application_version)
VALUES
    (1, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 1 , 'firebase_token', '', '', '', ''),
    (2, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C', 1 , 'firebase_token', '', '', '', ''),
    (3, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D', 1 , 'firebase_token', '', '', '', '');

INSERT INTO devices
    (id, user_guid, device_uuid, device_os, device_os_version, build_number, is_store_build, build_number_name, device_name)
VALUES
    (1, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'android', '', '200110', '', '2.6.0', ''),
    (2, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'android', '', '200111', '', '2.6.0', ''),
    (3, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'iPhone',  '', '200500', '', '2.6.0', '');

INSERT INTO push_notifications
    (id, intent, push_id, user_guid, created_at, updated_at, expired_at)
VALUES
    (1, 'new_offer', '00000000000000000000000000000001', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', '2021-08-17 14:00:00', '2021-08-17 14:00:00', '2021-08-17 14:10:00'),
    (2, 'new_offer', '00000000000000000000000000000002', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', '2021-08-17 14:00:00', '2021-08-17 14:00:00', '2077-01-01 14:00:00'),
    (3, 'new_offer', '00000000000000000000000000000003', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C', '2021-08-17 14:00:00', '2021-08-17 14:00:00', '2021-08-17 14:10:00'),
    (4, 'new_offer', '00000000000000000000000000000004', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D', '2021-08-17 14:00:00', '2021-08-17 14:00:00', '2021-08-17 14:10:00');
