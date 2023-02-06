BEGIN;

CREATE INDEX
    idx__order_cancel_reasons__matrix_id
    ON eats_compensations_matrix.order_cancel_reasons
    (matrix_id);

CREATE INDEX
    idx__order_cancel_reasons__group_id
    ON eats_compensations_matrix.order_cancel_reasons
    (group_id);

COMMIT;
