INSERT INTO
  safety_center.contacts(yandex_uid, contacts, created_at, updated_at)
VALUES
  (
    'user1'::text,
    ARRAY [('contact_1_1', '+79151234567_id')]::contact[],
    NOW(), NOW()
  ),
  (
    'user2'::text,
    ARRAY [('contact_2_1', '+79157654321_id')]::contact[],
    NOW(), NOW()
  );
