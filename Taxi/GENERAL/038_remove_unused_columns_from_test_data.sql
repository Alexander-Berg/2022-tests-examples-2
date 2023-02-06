BEGIN TRANSACTION;

ALTER TABLE test_data
    DROP COLUMN out_point_id,
    DROP COLUMN target_state,
    DROP COLUMN is_enabled;

COMMIT TRANSACTION;
