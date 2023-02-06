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
    'park_1',
    'setting_1',
    '{"value": {"val_str": "some_string_1", "val_number": 1}}',
    DEFAULT,
    DEFAULT
  ),
  (
    '100',
    'yandex',
    '',
    'setting_2',
    '{"value": 100}',
    DEFAULT,
    DEFAULT
  ),
  (
    '100',
    'yandex',
    'park_2',
    'setting_1',
     '{"value": {"val_str": "some_string_2", "val_number": 2}}',
    DEFAULT,
    DEFAULT
  )
;
