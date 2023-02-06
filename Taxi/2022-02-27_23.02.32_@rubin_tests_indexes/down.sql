/* downgrade database instructions */

ALTER TABLE "tests"
    DROP COLUMN "group"
;

DROP INDEX CONCURRENTLY IF EXISTS "tests_index1_idx";
DROP INDEX CONCURRENTLY IF EXISTS "tests_index2_idx";
DROP INDEX CONCURRENTLY IF EXISTS "tests_index4_idx";
DROP INDEX CONCURRENTLY IF EXISTS "tests_serial_idx";
DROP INDEX CONCURRENTLY IF EXISTS "tests_lsn_idx";
DROP INDEX CONCURRENTLY IF EXISTS "tests_created_serial_idx";
DROP INDEX CONCURRENTLY IF EXISTS "tests_test_id_group_idx";
DROP INDEX CONCURRENTLY IF EXISTS "tests_lsn_value_idx";
