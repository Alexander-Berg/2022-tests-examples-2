INSERT INTO secrets.secrets (
    key,
    secret_uuid, -- ID секрета в Секретнице
    version_uuid,
    updated,
    type,
    env
)
VALUES (
  'CAPITALS',
  'YAV_UUID_1',
  'VERSION_UUID_1',
  150,
  'mongodb',
  'unstable'
),
(
  'COUNTRIES',
  'YAV_UUID_2',
  'VERSION_UUID_2',
  450,
  'mongodb',
  'unstable'
);

INSERT INTO secrets.groups (
    name,
    secret_uuid, -- ID секрета в Секретнице
    version_uuid,
    env,
    service_name
)
VALUES (
  'taxi_unstable_imports',
  'YAV_UUID_3',
  'VERSION_UUID_4',
  'unstable',
  'imports'
);
