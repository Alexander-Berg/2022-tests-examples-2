INSERT INTO fleet_users.users (
    user_id,
    park_id,
    group_id,
    user_name,
    user_phone_id,
    created_at,
    is_enabled,
    is_confirmed,
    is_multifactor_authentication_required
) VALUES (
    'user_id1',
    'park_id',
    'admin',
    'Disp Dispovich',
    'phone_id1',
    '2021-01-01T00:00:00+00:00',
    true,
    false,
    false
), (
    'user_id2',
    'park_id',
    'dispatcher',
    'Dispa Dispovna',
    'phone_id2',
    '2021-01-01T00:00:00+00:00',
    false,
    false,
    false
), (
    'user_id_super',
    'park_id',
    'super',
    'Disp Dispovich',
    'phone_id_super',
    '2021-01-01T00:00:00+00:00',
    true,
    false,
    false
), (
    'user_id3',
    'park_id',
    'dispatcher',
    'Dispa Dispovna',
    'phone_id3',
    '2021-01-01T00:00:00+00:00',
    false,
    true,
    false
)
;
