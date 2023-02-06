INSERT INTO tlog.journal
(
    id,
    external_id,
    payload
)
VALUES
(1, '1', '{"amount": "1.6800", "account": {"currency": "EUR", "sub_account": "park_b2b_trip_payment"}, "created": "2019-07-09T12:42:15.731781+00:00", "details": {"due": "2019-06-14T10:17:29.000000+00:00", "alias_id": "deadbeef", "is_payable": true, "service_id": 651, "billing_client_id": "987654321", "handled_in_trust_flow": false, "service_transaction_id": null}, "entry_id": "1", "event_at": "2019-06-14T10:17:29.000000+00:00"}'),
(2, '2', '{"amount": "3.1415", "account": {"currency": "USD", "sub_account": "park_b2b_trip_payment"}, "created": "2019-10-04T12:42:15.731781+00:00", "details": {"due": "2019-10-04T10:17:29.000000+00:00", "alias_id": "cargo", "is_payable": true, "service_id": 651, "billing_client_id": "987654321", "handled_in_trust_flow": false, "tariff_class": "cargo"}, "entry_id": "1", "event_at": "2019-10-04T10:17:29.000000+00:00"}')
;
