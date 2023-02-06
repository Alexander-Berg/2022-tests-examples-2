UPSERT INTO `order_proc/indexes/order_proc_user_uid_request_due_index` (user_uid, order_id, is_anonymized, request_due)
VALUES
    (
        "uid_1",
        "order_id_1",
        false,
        Datetime("2008-08-08T00:06:00Z")
    ),
    (
        "uid_1",
        "order_id_2",
        false,
        Datetime("2014-03-18T04:30:00Z")
    ),
    (
        "uid_1",
        "order_id_50",
        false,
        Datetime("2050-01-01T00:00:00Z")
    ),
    (
        "uid_2",
        "order_id_3",
        false,
        DateTime("2022-02-24T04:30:00Z")
    );

