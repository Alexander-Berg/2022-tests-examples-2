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
  )
;
