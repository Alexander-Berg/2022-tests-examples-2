/* upgrade database instructions */

BEGIN;

ALTER TABLE "tests"
    ADD COLUMN "created"	TIMESTAMPTZ(0) NOT NULL DEFAULT NOW()
;

COMMENT ON COLUMN "tests"."created" IS 'Время создания';

COMMIT;
