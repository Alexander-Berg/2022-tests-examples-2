INSERT INTO latvia_rides_reports.order_income_events
    (entry_id, entity_external_id, agreement_id, sub_account, amount,
     event_at, stored_at, order_id, park_id, contractor_id, state)
VALUES
    (2, 'taximeter_driver_id/p2/c2', 'taxi/park_ride', 'payment/cash', '20.0000005',
     '2020-06-01T11:45+00', '2020-06-01T11:45+00', 'order2', 'p2', 'c2', 'NEW')
