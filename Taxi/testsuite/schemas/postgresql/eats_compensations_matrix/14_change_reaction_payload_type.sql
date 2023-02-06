BEGIN;

ALTER TABLE eats_compensations_matrix.order_cancel_reactions ALTER COLUMN payload TYPE JSONB USING payload::JSONB;
ALTER TABLE eats_compensations_matrix.order_cancel_reasons ALTER COLUMN code_ml DROP NOT NULL;

COMMIT;
