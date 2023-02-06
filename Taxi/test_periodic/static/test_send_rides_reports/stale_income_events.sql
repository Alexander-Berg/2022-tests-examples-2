INSERT INTO latvia_rides_reports.order_income_events
    (entry_id, entity_external_id, agreement_id, sub_account, amount,
     event_at, stored_at, order_id, park_id, contractor_id, state)
VALUES
    (1, 'taximeter_driver_id/p1/c1', 'taxi/park_ride', 'payment/cash', '10.0',
     '2020-06-01T00:00+00', '2020-06-01T00:00+00', 'order1', 'p1', 'c1', 'NEW')
