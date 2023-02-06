INSERT INTO `deletion_requests`
(yandex_uid, date_delete_since, date_delete_until, status, inserted_at, updated_at)
VALUES
    (
        "yandex_uid_1",
        DateTime("2012-03-01T18:22:03Z"),
        DateTime("2022-01-28T09:08:48Z"),
        "pending",
        CurrentUtcTimestamp(),
        CurrentUtcTimestamp()
    ),
    (
        "yandex_uid_1",
        NULL,
        DateTime("2012-03-01T18:22:03Z"),
        "sent_to_anonymizer",
        CurrentUtcTimestamp(),
        CurrentUtcTimestamp()
    );

