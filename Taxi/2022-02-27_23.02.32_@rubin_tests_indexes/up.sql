/* upgrade database instructions */

BEGIN;

ALTER TABLE "tests"
    ADD COLUMN "group"	TEXT
;

COMMENT ON COLUMN "tests"."group" IS 'Для выборки записей теста';

COMMIT;

CREATE INDEX CONCURRENTLY IF NOT EXISTS
    "tests_index1_idx"
ON
    "tests" ("value" DESC, "serial" DESC, "group")
;
CREATE INDEX CONCURRENTLY IF NOT EXISTS
    "tests_index2_idx"
ON
    "tests" ("value" DESC, "second_value" ASC, "serial" ASC, "group")
;
CREATE INDEX CONCURRENTLY IF NOT EXISTS
    "tests_index4_idx"
ON
    "tests" ("value" ASC, "second_value" DESC, "serial" ASC, "group")
;

CREATE INDEX CONCURRENTLY IF NOT EXISTS
    "tests_serial_idx"
ON
    "tests" ("serial" ASC, "group")
;
CREATE INDEX CONCURRENTLY IF NOT EXISTS
    "tests_lsn_idx"
ON
    "tests" ("lsn" ASC, "group")
;

CREATE INDEX CONCURRENTLY IF NOT EXISTS
    "tests_created_serial_idx"
ON
    "tests" ("created" ASC, "serial" ASC, "group")
;

CREATE INDEX CONCURRENTLY IF NOT EXISTS
    "tests_test_id_group_idx"
ON
    "tests" ("test_id" ASC, "group")
;
CREATE INDEX CONCURRENTLY IF NOT EXISTS
    "tests_lsn_value_idx"
ON
    "tests" ("lsn" ASC, "value")
;
