UPSERT INTO `order_proc_fields`
(
    order_id,
    json_path,
    original_value,
    anonymized_value,
    request_due,
    inserted_at,
    expires_at,
    committed
)
VALUES
    (
        "981f0ec03b763d9992d9329d1237205f",
        "order.creditcard.credentials.card_number",
        "400000****3692",
        "",
        CAST(1644246758000000 AS Timestamp),
        CurrentUtcTimestamp(),
        Null,
        False
    );
