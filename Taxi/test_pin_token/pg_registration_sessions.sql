INSERT INTO bank_userinfo.sessions (
    id,
    yandex_uid,
    phone_id,
    bank_uid,
    status,
    antifraud_info,
    created_at,
    updated_at,
    app_vars,
    locale
)
VALUES
(
    '00000000-0000-0000-0000-000000000001',
    '024e7db5-9bd6-4f45-a1cd-2a442e15bde1',
    '024e7db5-9bd6-4f45-a1cd-2a442e15bdf1',
    '7948e3a9-623c-4524-a390-9e4264d27a77',
    'not_registered',
    '{"device_id": "device_id",
      "dict": {"key": "value"}}'::jsonb,
    '2021-10-31T00:01:00+00:00',
    '2021-10-31T00:02:00+00:00',
    NULL,
    NULL
),
(
    '00000000-0000-0000-0000-000000000002',
    '024e7db5-9bd6-4f45-a1cd-2a442e15bde1',
    '024e7db5-9bd6-4f45-a1cd-2a442e15bdf1',
    '7948e3a9-623c-4524-a390-9e4264d27a77',
    'required_application_in_progress',
    '{"device_id": "device_id",
      "dict": {"key": "value"}}'::jsonb,
    '2021-10-31T00:01:00+00:00',
    '2021-10-31T00:02:00+00:00',
    NULL,
    NULL
);
