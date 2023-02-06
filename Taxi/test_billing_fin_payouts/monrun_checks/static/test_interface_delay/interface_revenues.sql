
insert into interface.revenues (
    id,
    created_at_utc,
    transaction_id,
    accounting_date,
    client_id,
    contract_id,
    currency,
    amount_tlog,
    amount,
    table_name,
    row_index,
    payload,
    status_code
)
values
(
    1,
    '2021-03-23T09:53:52.200001',
    12345,
    '2022-03-03T09:53:52.200001',
    '654321123',
    '123123',
    'RUB',
    13,
    111111,
    'qweqwe',
    123,
    ('[
      {
        "attr": 123
      }
    ]'::json),
    'SKIP_PAYOUT'
),
(
    2,
    '2021-03-04T09:53:52.200001',
    123456,
    '2022-03-04T09:53:52.200001',
    '64321123',
    '12123',
    'RUB',
    113,
    11111,
    'qweqwe',
    1223,
    '{}',
    'WITH_NETTING'
),
(
    3,
    '2022-03-16T09:53:52.200001',
    12345678,
    '2022-03-05T09:53:52.200001',
    '65434421123',
    '1223123',
    'RUB',
    123,
    111311,
    'qweqwe',
    1253,
    '{}',
    'IN_PROC'
),
(
    4,
    '2022-03-16T09:53:52.200001',
    12345679,
    '2022-03-05T09:53:52.200001',
    '65434421123',
    '1223123',
    'RUB',
    123,
    111311,
    'qweqwe',
    1253,
    '{}',
    'SKIP_PAYOUT'
),
(
    5,
    '2022-03-16T09:53:52.200001',
    12345680,
    '2022-03-05T09:53:52.200001',
    '65434421123',
    '1223123',
    'RUB',
    123,
    111311,
    'qweqwe',
    1253,
    '{}',
    'WITH_NETTING'
);