BEGIN;

ALTER TABLE eats_compensations_matrix.order_cancel_reasons
DROP COLUMN IF EXISTS code_ml;

COMMIT;
