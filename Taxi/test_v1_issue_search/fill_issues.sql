--!syntax_v1
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
    updated
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
    CAST('2021-09-06' AS Date),
    CAST('{"data":"value"}' AS Json),
    'description',
    CAST('2021-09-06' AS Date)
);
