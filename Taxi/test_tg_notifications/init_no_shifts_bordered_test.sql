INSERT INTO eats_logistics_performer_payouts.subjects (id, external_id, subject_type_id)
VALUES (1, '1', 2),
       (2, '2', 2);

INSERT INTO eats_logistics_performer_payouts.calculation_results (subject_id, meta) 
VALUES (1, '{"planned_start_at_local_tz": "2022-05-23T23:59:00+03:00", "verified_flg": "true", "calculation_schema": "eda_pickup_dropoff"}'::JSONB),
       (2, '{"planned_start_at_local_tz": "2022-05-25T00:01:00+03:00", "verified_flg": "true", "calculation_schema": "eda_pickup_dropoff"}'::JSONB);
