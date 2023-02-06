INSERT INTO
  safety_center.contacts(yandex_uid, contacts, created_at, updated_at)
VALUES
  (
    'MOCK_EXISTING_YANDEX_UID'::text,
    ARRAY [('foobar', '+79151234567_id')]::contact[],
    CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP),
    NOW()
  ),
  (
    'MOCK_ANOTHER_YANDEX_UID'::text,
    ARRAY [('barfoo', '+79157654321_id')]::contact[]::contact[],
    CAST('2018-01-01 10:00:00.000001' AS TIMESTAMP),
    NOW()
  );
