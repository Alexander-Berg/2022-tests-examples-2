INSERT INTO db.clients
  (
    consumer_id,
    client_id,
    key_salt,
    name,
    comment,
    creator_uid,
    creator_uid_provider,
    created_at,
    updated_at
  )
VALUES
  (
    'fleet-api-internal',
    'antontodua',
    'SaltSalt',
    'Антон Тодуа',
    'Для тестирования',
    '54591353',
    'yandex',
    current_timestamp,
    current_timestamp
  ),
  (
    'fleet-api',
    'taxi/park/abc',
    'S0ltS0lt',
    'Парк abc',
    'Для парка abc',
    '1120000000083978',
    'yandex-team',
    current_timestamp,
    current_timestamp
  )
;

INSERT INTO db.keys
  (
    client_id_,
    hash,
    is_enabled,
    entity_id,
    permission_ids,
    comment,
    creator_uid,
    creator_uid_provider,
    created_at,
    updated_at
  )
VALUES
  (
    1,
    'hash#1',
    true,
    'Ferrari-Land',
    '{}'::text[],
    'ключ без прав',
    '54591353',
    'yandex',
    '2018-02-26 19:11:13 +03:00',
    '2020-05-04 12:48:13 +03:00'
  ),
  (
    1,
    'hash#2',
    true,
    'Disneyland',
    '{"fleet-api:v1-users-list:POST","trash"}'::text[],
    'ключ с некорректным правом',
    '54591353',
    'yandex-team',
    '2018-02-27 15:43:13 +03:00',
    '2020-05-04 12:48:33 +03:00'
  ),
  (
    1,
    'hash#3',
    false,
    'Ferrari-Land',
    '{"fleet-api:v1-users-list:POST"}'::text[],
    'обычный отключенный ключ',
    '54591353',
    'yandex-team',
    '2018-02-27 15:49:13 +03:00',
    '2020-05-04 12:48:53 +03:00'
  )
;
