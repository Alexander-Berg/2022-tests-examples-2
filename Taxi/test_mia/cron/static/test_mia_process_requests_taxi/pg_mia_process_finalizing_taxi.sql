INSERT INTO
    mia.query(
        id,
        service_name,
        status,
        query,
        created_time,
        started_time
    )
VALUES (
    123,
    'taxi',
    'finalizing',
    '{"exact": {"order_id": "test_order_id"}, "period": {"created": {"from": "2019-03-03T20:56:35.450686", "to": "2019-04-05T20:56:35.450686"}}, "check_all_candidates": false}',
    '2020-02-20T13:02:33+00:00',
    '2020-02-20T13:02:33+00:00'
);

INSERT INTO mia.result(id, query_id, query_result)
VALUES (231, 123, '{"matched": [{"order_id": "test_order_id", "created": 1551722195.450, "created_idx": 1551722195}]}')
