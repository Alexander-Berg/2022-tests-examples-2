INSERT INTO latvia_rides_reports.order_income_events
    (entry_id, entity_external_id, agreement_id, sub_account, amount,
     event_at, stored_at, order_id, park_id, contractor_id, state)
VALUES
    (1, 'taximeter_driver_id/p1/c1', 'taxi/park_ride', 'payment/cash', '10.0',
     '2020-06-01T11:30+00', '2020-06-01T11:30+00', 'order1', 'p1', 'c1', 'FAILED'),
    (2, 'taximeter_driver_id/p2/c2', 'taxi/park_ride', 'payment/cash', '20.0000005',
     '2020-06-01T11:45+00', '2020-06-01T11:45+00', 'order2', 'p2', 'c2', 'NEW'),
    (3, 'taximeter_driver_id/p2/c2', 'taxi/park_ride', 'total/commission', '-5.0000015',
     '2020-06-01T12:00+00', '2020-06-01T12:00+00', 'order2', 'p2', 'c2', 'NEW'),
    (4, 'taximeter_driver_id/p2/c2', 'taxi/park_ride', 'unknown', '100.0',
     '2020-06-01T11:50+00', '2020-06-01T11:50+00', 'order2', 'p2', 'c2', 'NEW'),
    (10, 'taximeter_driver_id/p3/c3', 'taxi/park_ride', 'payment/cash', '30.0',
     '2020-06-01T12:00+00', '2020-06-01T12:00+00', 'order3', 'p3', 'c3', 'NEW')
