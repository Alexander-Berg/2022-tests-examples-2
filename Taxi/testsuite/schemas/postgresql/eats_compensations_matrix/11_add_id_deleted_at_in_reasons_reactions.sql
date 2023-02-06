BEGIN;

ALTER TABLE eats_compensations_matrix.order_cancel_reasons_reactions
ADD COLUMN id SERIAL PRIMARY KEY;

ALTER TABLE eats_compensations_matrix.order_cancel_reasons_reactions
ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;

COMMIT;
