INSERT INTO takeout.deletions (
        yandex_uid,
        data_category,
        status,
        deleted_at,
        status_updated_at,
        last_deletion_request_at
    )
VALUES (
        '12345',
        'taxi',
        'deleted',
        CAST('2018-01-01 12:00:00' AS TIMESTAMPTZ),
        CAST('2018-01-01 12:00:00' AS TIMESTAMPTZ),
        CAST('2018-01-01 10:00:00' AS TIMESTAMPTZ)
    );
