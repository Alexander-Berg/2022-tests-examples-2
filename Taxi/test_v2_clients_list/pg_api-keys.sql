INSERT INTO db.clients
  (
    id_,
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
    1,
    'fleet-api-internal',
    'opteum',
    '12AB34CD',
    'Оптеум',
    '',
    '54591353',
    'yandex',
    '2018-02-25 19:04:13 +03:00',
    '2018-02-25 19:04:13 +03:00'
  ),
  (
    2,
    'fleet-api-internal',
    'yandex_gas',
    'ABCD9876',
    'Яндекс.Заправки',
    '',
    '1120000000083978',
    'yandex-team',
    '2018-02-25 20:04:13 +03:00',
    '2018-02-25 20:04:13 +03:00'
  ),
  (
    3,
    'fleet-api',
    'vasya',
    'ABC',
    'Вася',
    '',
    '54591353',
    'yandex',
    '2018-02-26 14:55:13 +03:00',
    '2018-02-26 14:55:13 +03:00'
  ),
  (
    4,
    'fleet-api',
    'petya',
    'ABC',
    'Петя',
    '',
    '54591353',
    'yandex-team',
    '2018-02-26 14:56:13 +03:00',
    '2018-02-26 14:56:13 +03:00'
  ),
  (
    5,
    'fleet-api',
    'kolya',
    'ABC',
    'Коля',
    '',
    '1120000000083978',
    'yandex-team',
    '2018-02-26 14:57:13 +03:00',
    '2018-02-26 14:57:13 +03:00'
  ),
  (
    6,
    'fleet-api',
    'opteum',
    'ABC',
    'Оптеум внешний',
    '',
    '555',
    'yandex',
    '2018-02-26 15:12:13 +03:00',
    '2018-02-26 15:12:13 +03:00'
  )
;
