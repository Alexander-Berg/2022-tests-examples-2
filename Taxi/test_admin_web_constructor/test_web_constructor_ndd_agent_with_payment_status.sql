INSERT INTO cargo_finance.pay_applying_state(
    flow,
    entity_id,
    requested_sum2pay,
    final_result,
    using_debt_collector,
    is_final_result_paid
)
VALUES
    ('ndd_c2c',
    'ba05162748984b81affef7f6e92d96e2',
    '{
        "client": {
          "agent": {
            "sum": "987",
            "currency": "RUB"
          }
        }
    }',
    '{
        "client": {
          "agent": {
            "paid_sum": "987",
            "is_finished": true
          }
        }
    }',
     false,
     true
    );
