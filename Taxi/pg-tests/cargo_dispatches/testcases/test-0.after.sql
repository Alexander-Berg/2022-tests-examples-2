INSERT INTO dispatch.cargo_dispatches
    (dispatch_id, claim_id, is_current_claim, status_updated, claim_status, claim_version)
VALUES
    ('6776feef-01bb-400c-ab48-840fc00e0693'::UUID, 'claim_id3', FALSE, '2021-06-01T12:01:00.0000+03:00'::timestamptz, 'new', 1),
    ('6776feef-01bb-400c-ab48-840fc00e0694'::UUID, 'claim_id4', FALSE, '2021-06-01T12:02:00.0000+03:00'::timestamptz, 'new', 1),
    ('6776feef-01bb-400c-ab48-840fc00e0695'::UUID, 'claim_id5', FALSE, '2021-06-01T12:03:00.0000+03:00'::timestamptz, 'new', 1);
