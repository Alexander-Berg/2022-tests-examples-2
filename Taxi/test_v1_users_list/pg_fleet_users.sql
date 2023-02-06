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
    confirmed_at
) VALUES (
    'user_id1',
    'park_id1',
    'admin',
    'AUser Name',
    'phone_id1',
    '2021-01-01T00:00:00+00:00',
    true,
    false,
    false,
    null
),
(
    'user_id2',
    'park_id1',
    'super',
    'BUser Super',
    'phone_id2',
    '2021-01-01T00:00:00+00:00',
    true,
    false,
    false,
    null
)
;
