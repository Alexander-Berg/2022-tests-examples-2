INSERT INTO users
    (id, guid, first_name, last_name, msisdn, avatar, language_id)
VALUES
    (1234, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'first_name', 'last_name', 'msisdn', 'avatar', 1),
    (1235, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C', 'first_name', 'last_name', 'msisdn', 'avatar', 1);

INSERT INTO devices
    (id, user_guid, device_uuid, device_os, device_os_version, build_number, is_store_build, build_number_name, device_name)
VALUES
    (1, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'android', '', '100500', '', '2.6.0', ''),
    (2, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C', '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C', 'android', '', '100500', '', '2.6.0', '');
