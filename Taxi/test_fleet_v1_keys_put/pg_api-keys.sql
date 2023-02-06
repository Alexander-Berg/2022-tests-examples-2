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
    'fleet-api',
    'taxi/park/7ad36bc7560449998acbe2c57a75c293',
    'S1ltS1lt',
    'Парк 7ad36bc7560449998acbe2c57a75c293',
    'Для тестирования',
    '1120000000083978',
    'yandex-team',
    current_timestamp,
    current_timestamp
  ),
  (
    'test',
    'taxi/park/7ad36bc7560449998acbe2c57a75c293',
    'S1ltS1lt',
    'Парк 7ad36bc7560449998acbe2c57a75c293',
    'Для тестирования',
    '1120000000083978',
    'yandex-team',
    current_timestamp,
    current_timestamp
  )
;

INSERT INTO db.keys (
    id,
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
    '1',
    1,
    'S1ltS1lt',
    true,
    '7ad36bc7560449998acbe2c57a75c293',
    '{"fleet-api:v1-users-list:POST","trash"}'::text[],
    'комментарий',
    '54591353',
    'yandex',
    current_timestamp,
    current_timestamp
  ),
  (
    '2',
    2,
    'S1ltS1lt',
    true,
    '7ad36bc7560449998acbe2c57a75c293',
    '{"fleet-api:v1-users-list:POST","trash"}'::text[],
    'комментарий',
    '54591353',
    'yandex',
    current_timestamp,
    current_timestamp
  )
;
