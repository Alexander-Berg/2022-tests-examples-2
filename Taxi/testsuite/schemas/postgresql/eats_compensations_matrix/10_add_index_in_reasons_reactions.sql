BEGIN;

CREATE INDEX
    idx__order_cancel_reasons_reactions__reason_id
    ON eats_compensations_matrix.order_cancel_reasons_reactions
    (reason_id);

COMMIT;
