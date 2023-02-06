INSERT INTO `deletion_requests`
(yandex_uid, date_delete_since, date_delete_until, status, inserted_at, updated_at)
VALUES
    (
        "yandex_uid_2",
        DateTime("2010-01-01T00:00:00Z"),
        DateTime("2015-01-01T00:00:00Z"),
        "pending",
        CurrentUtcTimestamp(),
        CurrentUtcTimestamp()
    ),
    (
        "yandex_uid_3",
        NULL,
        DateTime("2015-01-01T00:00:00Z"),
        "sent_to_anonymizer",
        CurrentUtcTimestamp(),
        CurrentUtcTimestamp()
    );
