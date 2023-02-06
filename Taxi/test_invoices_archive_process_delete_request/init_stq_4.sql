INSERT INTO `deletion_requests`
(yandex_uid, date_delete_since, date_delete_until, status, inserted_at, updated_at)
VALUES
    (
        "yandex_uid_1",
        NULL,
        DateTime("2022-02-28T09:08:48Z"),
        "sent_to_anonymizer",
        CurrentUtcTimestamp(),
        CurrentUtcTimestamp()
    );
