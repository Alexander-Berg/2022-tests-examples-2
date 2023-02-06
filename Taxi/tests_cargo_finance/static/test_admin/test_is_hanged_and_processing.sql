INSERT INTO cargo_finance.pay_applying_state(
    flow,
    entity_id,
    created_at,
    last_modified_at,
    requested_sum2pay,
    last_applying_created_at,
    using_debt_collector
)
VALUES
    (
        'claims',
        '1001',
        '2021-10-28T13:54:41+0000',
        '2021-10-28T13:54:41+0000',
        '{"city": "Moscow"}',
        '2020-10-28T13:54:41+0000',
        true
    ),
    (
        'claims',
        '1002',
        '2021-10-28T10:54:41+0000',
        '2021-10-28T10:54:41+0000',
        '{"city": "Moscow"}',
        now(),
        false
    );
