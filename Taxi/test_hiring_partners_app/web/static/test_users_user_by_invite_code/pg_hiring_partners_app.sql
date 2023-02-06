
INSERT INTO hiring_partners_app.organizations(
    id,
    name,
    juridical_status,
    external_id
) VALUES (
    '0001',
    'Big Corporation, LLC',
    'LLC',
    NULL
);


INSERT INTO hiring_partners_app.users(
    personal_yandex_login_id,
    role,
    status,
    first_name,
    middle_name,
    last_name,
    personal_telegram_login_id,
    personal_phone_id,
    updated_by,
    created_at,
    updated_at,
    juridical_personality,
    cities,
    language_default,
    language_spoken,
    organization_id,
    meta_role
) VALUES (
    'YANDEXLOGIN_USER1',
    'user',
    'active',
    'Simple',
    'Office',
    'Guy',
    'tg_simple_id',
    'NBOSS_PERSONAL_PHONE_ID',
    'YANDEXLOGIN_ADMIN',
    '2020-09-13T13:00:00'::TIMESTAMP,
    '2020-09-14T13:00:00'::TIMESTAMP,
    'nvidia_physx',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    '0001',
    'agent'
);


INSERT INTO hiring_partners_app.invites(
    personal_yandex_login_id,
    code,
    activated_at
) VALUES (
    'YANDEXLOGIN_USER1',
    'user1_code1',
    '2022-07-13T13:00:00'::TIMESTAMP
),
(
    'YANDEXLOGIN_USER1',
    'user1_code2',
    '2022-07-12T13:00:00'::TIMESTAMP
);
