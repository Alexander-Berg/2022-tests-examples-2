INSERT INTO fees.draft_spec (change_doc_id, approvers, initiator, ticket)
VALUES ('TAXIBILLING-6770', '<scripts>', 'vvzakharov', 'TAXIBILLING-6770');

INSERT INTO fees.category (
    id,
    draft_spec_id,
    name,
    description,
    kind,
    product,
    detailed_product,
    fields,
    starts_at,
    ends_at
) SELECT
    '4b680b18-ce90-497d-8a52-eda14a55fe12',
    id,
    'Call Center Fee',
    'Комиссия за кол-центр: задаётся в виде абсолютного значения (надбавки) или ставки',
    'call_center',
    'order',
    'gross_commission_call_center_trips',
    'call_center',
    '2022-06-01T00:00:00+03:00',
    '2122-06-01T00:00:00+03:00'
FROM fees.draft_spec WHERE change_doc_id = 'TAXIBILLING-6770';

INSERT INTO fees.category_account(
    category_id, sub_account, agreement, currency, entity
) VALUES (
    '4b680b18-ce90-497d-8a52-eda14a55fe12', 'total', 'taxi/driver_balance', 'order_currency', 'taximeter_driver_id/{db_id}/{driver_id}'
), (
    '4b680b18-ce90-497d-8a52-eda14a55fe12', 'commission/callcenter', 'taxi/yandex_ride', 'order_currency', 'taximeter_driver_id/{db_id}/{driver_uuid}'
), (
    '4b680b18-ce90-497d-8a52-eda14a55fe12', 'commission/callcenter', 'taxi/yandex_ride', 'order_currency', 'taximeter_park_id/{db_id}'
);
