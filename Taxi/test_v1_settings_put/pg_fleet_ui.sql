INSERT INTO
  fleet_ui.user_settings (
    passport_uid,
    provider,
    park_id,
    key,
    data,
    created_at,
    updated_at
  )
VALUES
  (
    '100',
    'yandex',
    'park_id',
    '1_setting_string',
    '{"value": "old_string_value"}',
    DEFAULT,
    DEFAULT
  )
;
