--!syntax_v1
$_current_utc_timestamp = CurrentUtcTimestamp();

-- create new event
REPLACE INTO issues (
    -- key
    invoice_id_hash,
    invoice_id,
    namespace_id,
    kind,
    target,
    external_id,
    -- end key
    counter,
    payload,
    description,
    created,
    payload_updated,
    description_updated,
    updated,
    amount,
    currency
) VALUES (
    -- key
    1637787580375664568,
    'invoice_id',
    'namespace_id',
    'kind2',
    'compensation_refund',
    'external_id',
    -- end key
    1,
     CAST('{"data":"value"}' AS Json),
    'description',
    $_current_utc_timestamp,
    CAST('{"data":"value", "status": "clear_pending"}' AS Json),
    'description',
    $_current_utc_timestamp,
    "500",
    "RUB"
);
