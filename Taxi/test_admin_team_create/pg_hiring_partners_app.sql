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
    '0000'
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
    'j9r2jgig92if32hfdsfh8fh2u23uh328',
    'superuser',
    'active',
    'Super',
    'Puper',
    'Boss',
    'tg_bboss_id',
    '1104248e26074dd88e46f350037459fa',
    'dwoqwqpkokoe0fmsdofjiweewfi9ewfs',
    '2020-09-13T13:00:00'::TIMESTAMP,
    '2020-09-14T13:00:00'::TIMESTAMP,
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    0,
    '0000',
    'agent'
),
(
    'a95c01defa9d4909910e084cbdabecca',
    'user',
    'active',
    'Just',
    'Simple',
    'User',
    'tg_simple_user',
    'be5da8c4f4c741afa8887c41502c441b',
    'j9r2jgig92if32hfdsfh8fh2u23uh328',
    '2020-09-13T13:00:00'::TIMESTAMP,
    '2020-09-14T13:00:00'::TIMESTAMP,
    'physical_person',
    ARRAY[]::TEXT[],
    'ru',
    ARRAY['ru'],
    0,
    '0000',
    'agent'
)
;
