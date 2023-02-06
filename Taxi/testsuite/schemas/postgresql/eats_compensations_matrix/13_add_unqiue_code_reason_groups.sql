BEGIN;

ALTER TABLE eats_compensations_matrix.order_cancel_reason_groups
ADD UNIQUE (code);

COMMIT;
