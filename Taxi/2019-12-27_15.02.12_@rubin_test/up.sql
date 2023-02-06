/* upgrade database instructions */

BEGIN;

CREATE TABLE "tests" (
    "test_id"       TEXT PRIMARY KEY,
    "value"         TEXT,
    "lsn"           BIGSERIAL,
    "serial"        BIGSERIAL
);

COMMENT ON COLUMN "tests"."test_id" IS 'Идентификатор';
COMMENT ON COLUMN "tests"."value"   IS 'Значение';
COMMENT ON COLUMN "tests"."lsn"     IS 'Номер изменения в шарде';
COMMENT ON COLUMN "tests"."serial"  IS 'Последовательный идентификатор в шарде';

COMMIT;
