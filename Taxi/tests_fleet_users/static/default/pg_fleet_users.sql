INSERT INTO fleet_users.users (
    user_id,
    park_id,
    group_id,
    user_name,
    user_phone_id,
    created_at,
    is_enabled,
    is_confirmed,
    is_multifactor_authentication_required,
    confirmed_at,
    passport_uid,
    passport_name
) VALUES (
    'user_id1',
    '111',
    '333',
    'Дисп Диспович',
    'phone_id1',
    '2021-01-01T00:00:00+00:00',
    true,
    false,
    false,
    null,
    null,
    null
), (
    'user_id2',
    '222',
    '444',
    'Дисп Диспович',
    'phone_id1',
    '2021-01-01T00:00:00+00:00',
    true,
    false,
    false,
    null,
    null,
    null
), (
    'user_id3',
    '333',
    '444',
    'Дисп Диспович',
    'phone_id1',
    '2021-01-01T00:00:00+00:00',
    true,
    true,
    false,
    '2021-01-02T00:00:00+00:00',
    'passport_uid3',
    'John Smith'
), (
    'user_id4',
    '444',
    '444',
    'Дисп Диспович',
    'phone_id1',
    '2021-01-01T00:00:00+00:00',
    false,
    false,
    false,
    null,
    null,
    null
), (
    'user_id5',
    'park_id',
    '444',
    'Дисп Диспович',
    'phone_id2',
    '2021-01-01T00:00:00+00:00',
    false,
    false,
    false,
    null,
    null,
    null
)
;
