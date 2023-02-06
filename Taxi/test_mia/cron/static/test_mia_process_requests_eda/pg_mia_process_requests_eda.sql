INSERT INTO mia.query(id, service_name, status, query, created_time, started_time)
VALUES
(123, 'eda', 'in_progress', '{"exact": {"order_id": 102}, "completed_only": false}', '2020-02-20T13:02:33+00:00', '2020-02-20T13:02:33+00:00');

INSERT INTO mia.result(id, query_id, query_result)
VALUES
(231, 123, '{"operation_id": "some_operation_id"}')
