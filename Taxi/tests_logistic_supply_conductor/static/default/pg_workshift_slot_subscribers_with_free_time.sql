INSERT INTO logistic_supply_conductor.workshift_slot_subscribers
    (slot_id, contractor_id, subscribed_at, idempotency,
    free_time_left, free_time_end, out_of_polygon_time_end)
VALUES
(
    3,
    ('929f5bc2f0f44c8595faaa818f4d3ab8', '31d323d5532440de8a82ee2e2e2e7b5f'),
    '2033-04-08T23:59:00Z',
    'idempotency_token',
    '3 hours'::interval,
    NULL,
    NULL
),
(
    3,
    ('c3ad7a1fdc1a48ef9cb121f457e5a5e0', '4a90810b6b2b446bbafa7f2f14fa2010'),
    '2033-04-08T23:59:00Z',
    'idempotency_token',
    NULL,
    '2033-04-09T05:00:00Z',
    NULL
),
(
    3,
    ('12abe2811d6249fda94a962afa8fd129', '30cd94f445454aeba36f382085f9bb03'),
    '2033-04-08T23:59:00Z',
    'idempotency_token',
    '2 hours'::interval,
    NULL,
    NULL
),
(
    3,
    ('5a385e661c8a46e5a575dd9474e49db7', 'e79301f26fe842e398bb752aa6381816'),
    '2033-04-08T23:59:00Z',
    'idempotency_token',
    NULL,
    '2033-04-09T06:00:00Z',
    NULL
),
(
    3,
    ('20f72c73435f4c0ebd559188a2e7f893', 'e6f286baf6594ce9855b08c088a365d2'),
    '2033-04-08T23:59:00Z',
    'idempotency_token',
    '1 hours'::interval,
    NULL,
    NULL
),
(
    3,
    ('9b6ef7a02fe24119a7b2a191caf5ed82', 'b7023161d1ef4e16ad855b6d7a6173bd'),
    '2033-04-08T23:59:01Z',
    'idempotency_token',
    '8 hours'::interval,
    NULL,
    NULL
),
(
    3,
    ('845f055e7f46459b99917e91418e8896', 'b84f6d32423747f4a691270c2b61ce4d'),
    '2033-04-08T23:59:00Z',
    'idempotency_token',
    NULL,
    '2033-04-09T00:00:01Z',
    NULL
),
(
    3,
    ('74174e1784e340e7a56b949a290b9aea', 'fb18bcb2f7ce426fa11b3dd86d20f1c1'),
    '2033-04-08T23:59:00Z',
    'idempotency_token',
    '9 hours'::interval,
    NULL,
    '2033-04-09T00:05:00Z'
),
(
    3,
    ('064ffd76903746cba731cae5d33172f4', '02113168e5e94418bf8b3c9724678c84'),
    '2033-04-08T23:59:00Z',
    'idempotency_token',
    '10 hours'::interval,
    NULL,
    '2033-04-09T00:05:00Z'
);
