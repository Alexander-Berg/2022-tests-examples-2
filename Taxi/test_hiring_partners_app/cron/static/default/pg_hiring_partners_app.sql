
INSERT INTO hiring_partners_app.organizations(
    id,
    name,
    juridical_status,
    external_id
) VALUES (
    '0000',
    'Массажный салон Офелия',
    'ИП',
    NULL
),
(
    '0001',
    'Big Corporation, LLC',
    'LLC',
    NULL
),
(
    '0002',
    'Taxi Mystery',
    'LLC',
    'TEST_TAXIPARK_ID'
);


INSERT INTO hiring_partners_app.permissions_groups(
    id,
    definition,
    organization_id,
    is_default_for_organization
) VALUES (
    1000,
    '{}'::jsonb,
    '0001',
    TRUE
),
(
    1001,
    '{}'::jsonb,
    NULL,
    FALSE
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
    permissions_group_id,
    organization_id,
    meta_role
) VALUES (
    'YANDEXLOGIN1',
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
    1000,
    '0001',
    'agent'
),
(
    'YANDEXLOGIN2',
    'user',
    'active',
    'Simple',
    'Office',
    'Taxipark',
    'tg_taxipark_id',
    'TAXIPARK_PERSONAL_PHONE_ID',
    'YANDEXLOGIN_ADMIN',
    '2020-09-13T13:00:00'::TIMESTAMP,
    '2020-09-14T13:00:00'::TIMESTAMP,
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    1000,
    '0001',
    'agent'
),
(
    'YANDEXLOGIN_USER_NOT_ACTIVE',
    'user',
    'deactivated',
    'Simple',
    'Office',
    'Taxipark',
    'tg_taxipark_id',
    'TAXIPARK_PERSONAL_PHONE_ID',
    'YANDEXLOGIN_ADMIN',
    '2020-09-13T13:00:00'::TIMESTAMP,
    '2020-09-14T13:00:00'::TIMESTAMP,
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    1000,
    '0001',
    'agent'
),
(
    'YANDEXLOGIN_EXISTING',
    'user',
    'deactivated',
    'Simple',
    'Office',
    'Taxipark',
    'tg_taxipark_id',
    'TAXIPARK_PERSONAL_PHONE_ID',
    'YANDEXLOGIN_ADMIN',
    '2020-09-13T13:00:00'::TIMESTAMP,
    '2020-09-14T13:00:00'::TIMESTAMP,
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    1000,
    '0001',
    'agent'
);
