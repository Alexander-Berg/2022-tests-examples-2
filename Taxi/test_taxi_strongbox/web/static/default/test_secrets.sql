INSERT INTO secrets.groups (
  name,
  secret_uuid,
  version_uuid,
  env,
  service_name
)
VALUES (
  'test_group_1',
  'auth_secret_uuid_1',
  'auth_version_uuid_1',
  'unstable',
  'test_service'
),
(
  'test_group_3',
  'auth_secret_uuid_3',
  'auth_version_uuid_3',
  'unstable',
  'test_service_1'
),
(
  'test_group_5',
  'auth_secret_uuid_5',
  'auth_version_uuid_5',
  'unstable',
  'test_service_2'
),
(
  'test_group_6',
  'auth_secret_uuid_6',
  'auth_version_uuid_6',
  'unstable',
  'test_service_3'
),
(
  'test_group_7',
  'auth_secret_uuid_7',
  'auth_version_uuid_7',
  'unstable',
  'test_service_6'
),
(
  'test_group_8',
  'auth_secret_uuid_8',
  'auth_version_uuid_8',
  'unstable',
  'test_service_4'
),
(
  'test_group_9',
  'auth_secret_uuid_9',
  'auth_version_uuid_9',
  'testing',
  'test_service_2'
),
(
  'test_group_10',
  'auth_secret_uuid_10',
  'auth_version_uuid_10',
  'unstable',
  'test_service_5'
),
(
  'taxi:some-service:unstable',
  'auth_secret_uuid_5',
  'auth_version_uuid_5',
  'unstable',
  'test_service_2'
);

INSERT INTO secrets.templates (
  service_name,
  type_name,
  content,
  updated
)
VALUES (
  'test_service_1',
  'secdist',
  'mongo_settings',
  150
),
(
  'test_service_2',
  'secdist',
  '{{ TEST_1 }}',
  150
),
(
  'test_service_3',
  'secdist',
  '{{ UNKNOWN }}',
  150
),
(
  'test_service_4',
  'secdist',
  '{{{ TEST_2 }}',
  150
),
(
  'test_service_5',
  'secdist',
  '{{ TEST_1 }}',
  350
),
(
  'test_service_6',
  'secdist',
  '{{ TEST_2 }}',
  150
),
(
  '_default',
  'audit_secrets',
  'really common audit secret',
  150
),
(
  'test_service_1',
  'pilorama_secrets',
  'elastic credentials',
  150
);

INSERT INTO secrets.secrets (
    key,
    secret_uuid, -- ID секрета в Секретнице
    version_uuid,
    type,
    updated,
    env,
    tplatform_namespace,
    project_name,
    service_name,
    idempotency_token
)
VALUES (
  'TEST_1',
  'YAV_UUID_1',
  'VERSION_UUID_1',
  'mongodb',
  250,
  'unstable',
  null,
  null,
  null,
  null
),
(
  'TEST_2',
  'YAV_UUID_2',
  'VERSION_UUID_2',
  'mongodb',
  250,
  'unstable',
  'taxi',
  'meow',
  null,
  null
),
(
  'MONGODB_TAXI_STRONGBOX',
  'YAV_UUID_2',
  'VERSION_UUID_2',
  'postgresql',
  250,
  'testing',
  null,
  null,
  null,
  null
),
(
  'SEARCHABLE_SECRET',
  'YAV_UUID_2',
  'VERSION_UUID_2',
  'mongodb',
  250,
  'testing',
  'taxi',
  'taxi',
  null,
  'idempotency_token_1'
),
(
  'SEARCHABLE_SECRET',
  'YAV_UUID_2',
  'VERSION_UUID_2',
  'redis',
  250,
  'unstable',
  'taxi',
  'taxi',
  'service',
  null
),
(
  'SEARCH_ABLE_SECRET_2',
  'YAV_UUID_2',
  'VERSION_UUID_2',
  'api_token',
  250,
  'production',
  'taxi',
  'taxi-infra',
  'service-2',
  null
),
(
  'SEARCH_ABLE_SECRET_2',
  'YAV_UUID_2',
  'VERSION_UUID_2',
  'api_token',
  250,
  'testing',
  'taxi',
  'taxi-infra',
  'service-2',
  null
),
(
  'TVM_ACCESS_SECRET',
  'YAV_UUID_3',
  'VERSION_UUID_3',
  'api_token',
  250,
  'production',
  'taxi',
  'taxi-infra',
  'service-2',
  null
),
(
  'POSTGRES_TAXI_STRONGBOX',
  'YAV_UUID_PG_2',
  'VERSION_UUID_PG_2',
  'postgresql',
  250,
  'testing',
  null,
  'project_name',
  'service_name',
  null
);

INSERT INTO secrets.scope_rights (
    tplatform_namespace, project_name, service_name, env, login, role_type
)
VALUES
    ('taxi', 'taxi-infra', 'service-2', 'production', 'some-mate', 'edit_secrets'),
    ('taxi', 'taxi-infra', 'service-2', 'testing', 'some-mate', 'edit_secrets'),
    ('taxi', 'taxi', null, 'testing', 'some-mate', 'edit_secrets'),
    ('taxi', 'taxi', 'service', 'testing', 'some-mate', 'edit_secrets'),
    (null, null, null, 'unstable', 'some-mate', 'edit_secrets'),

    ('taxi', 'taxi-infra', null, 'testing', 'some-mate-2', 'edit_secrets'),
    (null, null, null, 'testing', 'some-mate-2', 'edit_secrets'),
    ('taxi', 'taxi', null, 'unstable', 'some-mate-2', 'edit_secrets'),

    ('taxi', 'taxi', 'service', 'testing', 'some-mate-3', 'edit_secrets'),
    ('taxi', 'taxi', 'service', 'unstable', 'some-mate-3', 'edit_secrets'),

    ('taxi', 'taxi-infra', 'service-2', 'production', 'some-mate', 'create_secrets'),
    ('taxi', 'taxi-infra', 'service-2', 'testing', 'some-mate', 'create_secrets'),
    ('taxi', 'taxi', null, 'testing', 'some-mate', 'create_secrets'),
    ('taxi', 'taxi', 'service', 'testing', 'some-mate', 'create_secrets'),
    ('taxi', null, null, 'unstable', 'some-mate', 'create_secrets'),

    ('taxi', 'taxi-infra', null, 'testing', 'some-mate-2', 'create_secrets'),
    ('taxi', null, null, 'testing', 'some-mate-2', 'create_secrets'),
    ('taxi', 'taxi', null, 'unstable', 'some-mate-2', 'create_secrets'),

    ('taxi', 'taxi', 'service', 'testing', 'some-mate-3', 'create_secrets'),
    ('taxi', 'taxi', 'service', 'unstable', 'some-mate-3', 'create_secrets'),

    ('taxi', 'taxi-infra', null, 'unstable', 'some-mate-4', 'create_secrets'),
    ('taxi', 'taxi-infra', null, 'unstable', 'some-mate-4', 'edit_secrets'),

    ('taxi', 'taxi', 'service', 'production', 'only-create', 'create_secrets'),
    ('taxi', 'taxi', 'service', 'testing', 'only-create', 'create_secrets'),
    ('taxi', 'taxi', 'service', 'unstable', 'only-create', 'create_secrets')
;

INSERT INTO secrets.tvm_access (
  service_name,
  secret_key,
  env
)
VALUES (
  'replication',
  'TVM_ACCESS_SECRET',
  'production'
);


INSERT INTO secrets.secrets_templates (
    secret_id,
    template_id
)
VALUES (
    2,
    2
);
