
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
    'have_invite_link_permission_pd_id',
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
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    '0001',
    'eats_freelancer'
),
(
    'not_have_invite_link_permission_pd_id',
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
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    '0001',
    'eats_freelancer'
),
(
    'user_without_code_pd_id',
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
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    '0001',
    'eats_freelancer'
);


INSERT INTO hiring_partners_app.invites(
    personal_yandex_login_id,
    code,
    activated_at
) VALUES (
    'have_invite_link_permission_pd_id',
    'user1_code1',
    '2022-07-13T13:00:00'::TIMESTAMP
);
