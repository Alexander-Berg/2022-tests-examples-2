BEGIN;

ALTER TABLE eats_compensations_matrix.order_cancel_matrices
    ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE eats_compensations_matrix.order_cancel_reason_groups
    ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE eats_compensations_matrix.order_cancel_reasons
    ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE eats_compensations_matrix.order_cancel_reactions
    ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;

COMMIT;
