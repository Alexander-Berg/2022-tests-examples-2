INSERT INTO 
    cargo_finance.pay_applying_state (
        flow, 
        entity_id, 
        requested_sum2pay, 
        using_debt_collector,
        last_applying_created_at
    )
VALUES
    ('claims', '123', '{}', FALSE, now()),
    ('claims', '124', '{}', TRUE, NULL),
    ('taxiparks', '123', '{}', FALSE, now() - '1 day'::interval),
    ('taxiparks', '124', '{}', FALSE, NULL),
    ('taxiparks', '125', '{}', FALSE, now())
