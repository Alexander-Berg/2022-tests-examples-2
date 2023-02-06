
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
    organization_id
) VALUES (
    0,
    '{
      "allowed_vacancies": [
        "courier_eda",
        "courier_lavka"
      ],
      "allowed_groups": {
        "supervisors": [],
        "users": [
          "__self__"
        ]
      }
    }'::jsonb,
    '0001'
),
(
    1,
    '{
      "allowed_vacancies": [
        "courier_eda",
        "courier_lavka"
      ],
      "allowed_groups": {
        "supervisors": [
          "YANDEXLOGIN_HEAD1_1",
          "YANDEXLOGIN_HEAD1_2"
        ],
        "users": [
          "__self__"
        ]
      }
    }'::jsonb,
    '0001'
),
(
    2,
    '{
      "allowed_vacancies": [
        "courier_eda",
        "courier_lavka"
      ],
      "allowed_groups": {
        "supervisors": [
          "YANDEXLOGIN_USER1",
          "YANDEXLOGIN_USER2",
          "YANDEXLOGIN_USER3"
        ],
        "users": [
          "__self__"
        ]
      }
    }'::jsonb,
    '0001'
),
(
    3,
    '{
      "allowed_vacancies": [
        "courier_eda",
        "courier_lavka"
      ],
      "allowed_groups": {
        "supervisors": [
          "YANDEXLOGIN_USER3",
          "YANDEXLOGIN_USER4"
        ],
        "users": [
          "__self__"
        ]
      }
    }'::jsonb,
    '0001'
),
(
    4,
    '{
      "allowed_vacancies": [
        "courier_eda",
        "courier_lavka"
      ],
      "allowed_groups": {
        "supervisors": [
          "YANDEXLOGIN_HEAD1_2",
          "YANDEXLOGIN_HEAD2_2"
        ],
        "users": [
          "__self__"
        ]
      }
    }'::jsonb,
    '0001'
),
(
    5,
    '{
      "allowed_vacancies": [
        "driver"
      ],
      "allowed_groups": {
        "customer": "TEST_TAXIPARK_ID"
      }
    }'::jsonb,
    '0002'
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
    'YANDEXLOGIN_HEAD2_1',
    'user',
    'active',
    'Big',
    'Big',
    'Boss',
    'tg_bboss_id',
    'BBOSS_PERSONAL_PHONE_ID',
    'YANDEXLOGIN_ADMIN',
    '2020-09-13T13:00:00'::TIMESTAMP,
    '2020-09-14T13:00:00'::TIMESTAMP,
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    1,
    '0001',
    'agent'
),
(
    'YANDEXLOGIN_HEAD2_2',
    'user',
    'active',
    'Big',
    'Big',
    'Boss2',
    'tg_bboss2_with_circular_id',
    'BBOSS_PERSONAL_PHONE_ID',
    'YANDEXLOGIN_ADMIN',
    '2020-09-13T13:00:00'::TIMESTAMP,
    '2020-09-14T13:00:00'::TIMESTAMP,
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    4,
    '0001',
    'agent'
),
(
    'YANDEXLOGIN_HEAD1_1',
    'user',
    'active',
    'Not',
    'Big',
    'Boss',
    'tg_nboss_id',
    'NBOSS_PERSONAL_PHONE_ID',
    'YANDEXLOGIN_ADMIN',
    '2020-09-13T13:00:00'::TIMESTAMP,
    '2020-09-14T13:00:00'::TIMESTAMP,
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    2,
    '0001',
    'agent'
),
(
    'YANDEXLOGIN_HEAD1_2',
    'user',
    'active',
    'Not',
    'Big',
    'Boss2',
    'tg_nboss2_id',
    'NBOSS_PERSONAL_PHONE_ID',
    'YANDEXLOGIN_ADMIN',
    '2020-09-13T13:00:00'::TIMESTAMP,
    '2020-09-14T13:00:00'::TIMESTAMP,
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    3,
    '0001',
    'agent'
),
(
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
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    0,
    '0001',
    'agent'
),
(
    'YANDEXLOGIN_USER2',
    'user',
    'active',
    'Simple',
    'Office',
    'Guy2',
    'tg_simple2_id',
    'NBOSS_PERSONAL_PHONE_ID',
    'YANDEXLOGIN_ADMIN',
    '2020-09-13T13:00:00'::TIMESTAMP,
    '2020-09-14T13:00:00'::TIMESTAMP,
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    0,
    '0001',
    'agent'
),
(
    'YANDEXLOGIN_USER3',
    'user',
    'active',
    'Simple',
    'Office',
    'Guy3',
    'tg_simple3_id',
    'NBOSS_PERSONAL_PHONE_ID',
    'YANDEXLOGIN_ADMIN',
    '2020-09-13T13:00:00'::TIMESTAMP,
    '2020-09-14T13:00:00'::TIMESTAMP,
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    0,
    '0001',
    'agent'
),
(
    'YANDEXLOGIN_USER4',
    'user',
    'active',
    'Simple',
    'Office',
    'Guy4',
    'tg_simple4_id',
    'NBOSS_PERSONAL_PHONE_ID',
    'YANDEXLOGIN_ADMIN',
    '2020-09-13T13:00:00'::TIMESTAMP,
    '2020-09-14T13:00:00'::TIMESTAMP,
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    0,
    '0001',
    'agent'
);
