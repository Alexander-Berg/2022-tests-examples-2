INSERT INTO ridehistory.takeout_job_result
    (request_id, result_json)
VALUES
    ('1', '[{"some": ["random", "json"]}]'::jsonb),
    ('2', NULL);
