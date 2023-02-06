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
        '024e7db5-9bd6-4f45-a1cd-0a442e15bde1',
        '024e7db5-9bd6-4f45-a1cd-0a442e15bdf2',
        '7948e3a9-623c-4524-a390-0e4264d27a77',
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
        '024e7db5-9bd6-4f45-a1cd-0a442e15bde1',
        '024e7db5-9bd6-4f45-a1cd-0a442e15bdf2',
        '7948e3a9-623c-4524-a390-0e4264d27a77',
        'required_application_in_progress',
        '{"device_id": "device_id",
          "dict": {"key": "value"}}'::jsonb,
        '2021-10-31T00:01:00+00:00',
        '2021-10-31T00:02:00+00:00',
        NULL,
        NULL
    );

INSERT INTO bank_userinfo.deleted_sessions (
    id,
    deleted_session_id,
    yandex_uid,
    phone_id,
    bank_uid,
    status,
    antifraud_info,
    created_at,
    updated_at,
    app_vars,
    locale,
    deleted_at
)
VALUES
    (
        '00000000-0000-0000-0000-100000000001',
        '00000000-0000-0000-1000-100000000001',
        '024e7db5-9bd6-4f45-a1cd-1a442e15bde1',
        '024e7db5-9bd6-4f45-a1cd-1a442e15bdf2',
        '7948e3a9-623c-4524-a390-1e4264d27a77',
        'not_registered',
        '{"device_id": "device_id",
          "dict": {"key": "value"}}'::jsonb,
        '2021-10-31T00:11:00+00:00',
        '2021-10-31T00:12:00+00:00',
        NULL,
        NULL,
        '2021-11-01T00:11:00+00:00'
    ),
    (
        '00000000-0000-0000-0000-100000000002',
        '00000000-0000-0000-1000-100000000002',
        '024e7db5-9bd6-4f45-a1cd-1a442e15bde1',
        '024e7db5-9bd6-4f45-a1cd-1a442e15bdf2',
        '7948e3a9-623c-4524-a390-1e4264d27a77',
        'required_application_in_progress',
        '{"device_id": "device_id",
          "dict": {"key": "value"}}'::jsonb,
        '2021-10-31T00:21:00+00:00',
        '2021-10-31T00:22:00+00:00',
        NULL,
        NULL,
        '2021-11-01T00:12:00+00:00'
    );
