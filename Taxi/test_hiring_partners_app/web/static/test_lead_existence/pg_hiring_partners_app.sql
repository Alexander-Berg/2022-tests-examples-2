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
    'a95c01defa9d4909910e084cbdabecca',
    'user',
    'active',
    'Big',
    'Big',
    'Boss',
    'tg_bboss_id',
    'df26389528dd429a903d59f731ccf6b4',
    'j9r2jgig92if32hfdsfh8fh2u23uh328',
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
    'jr2r8gudfghlfdskmi9u322104re3fiw',
    'user',
    'active',
    'Big',
    'Big',
    'Boss2',
    'tg_bboss2_with_circular_id',
    '6749538458d64102a3c7efedc179ae45',
    'j9r2jgig92if32hfdsfh8fh2u23uh328',
    '2020-09-13T13:00:00'::TIMESTAMP,
    '2020-09-14T13:00:00'::TIMESTAMP,
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    4,
    '0001',
    'scout'
),
(
    'nfjew9r3i9rnfdv934u843ry8hr89gh9',
    'user',
    'active',
    'Yet',
    'Another',
    'User',
    'tg_yauser__id',
    '6749538458d64102a3c7efedc179ae45',
    'j9r2jgig92if32hfdsfh8fh2u23uh328',
    '2020-09-13T13:00:00'::TIMESTAMP,
    '2020-09-14T13:00:00'::TIMESTAMP,
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    4,
    '0001',
    'eats_freelancer'
)
;
