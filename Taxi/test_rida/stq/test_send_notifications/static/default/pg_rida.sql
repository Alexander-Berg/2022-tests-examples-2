INSERT INTO users
    (id, guid, is_received_push_notification, first_name, last_name, msisdn, avatar, language_id)
VALUES
    (1234, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', TRUE, 'first_name', 'last_name', 'msisdn', 'avatar', 1),
    (5678, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G', TRUE, 'first_name', 'last_name', 'msisdn', 'avatar', 1),
    (3456, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5J', FALSE, 'first_name', 'last_name', 'msisdn', 'avatar', 1);

INSERT INTO devices
    (id, user_guid, device_uuid, device_os, device_os_version, build_number, is_store_build, build_number_name, device_name)
VALUES
    (1, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'android', '', '200110', '', '2.6.0', ''),
    (2, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'android', '', '200111', '', '2.6.0', ''),
    (3, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5J', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'iPhone',  '', '200500', '', '2.6.0', '');


INSERT INTO push_notification_tokens
    (id, user_guid, language_id, token, hash, device_type, application_id, application_version)
VALUES
    (1234, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 1 , 'firebase_token0', '', '', '', ''),
    (5678, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G', 1, 'firebase_token1', '', '', '', ''),
    (3456, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5J', 1, 'firebase_token2', '', '', '', '');
