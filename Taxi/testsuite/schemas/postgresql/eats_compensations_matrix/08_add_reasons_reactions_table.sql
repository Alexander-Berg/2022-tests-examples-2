TRUNCATE TABLE eats_compensations_matrix.order_cancel_reasons CASCADE;
TRUNCATE TABLE eats_compensations_matrix.order_cancel_reactions CASCADE;

ALTER TABLE eats_compensations_matrix.order_cancel_reasons
ADD COLUMN IF NOT EXISTS code_ml VARCHAR(255) NOT NULL,
ADD COLUMN IF NOT EXISTS payment_type INTEGER NOT NULL,
ADD COLUMN IF NOT EXISTS allowed_callers INTEGER NOT NULL,
ADD COLUMN IF NOT EXISTS allowed_countries TEXT[] NOT NULL,
DROP COLUMN IF EXISTS is_system
;

ALTER TABLE eats_compensations_matrix.order_cancel_reactions
DROP COLUMN IF EXISTS reason_id,
DROP COLUMN IF EXISTS name,
DROP COLUMN IF EXISTS is_transferred,
DROP COLUMN IF EXISTS auto
;


CREATE TABLE IF NOT EXISTS eats_compensations_matrix.order_cancel_reasons_reactions
(
    reason_id INTEGER REFERENCES eats_compensations_matrix.order_cancel_reasons(id) ON DELETE CASCADE,
    reaction_id INTEGER REFERENCES eats_compensations_matrix.order_cancel_reactions(id) ON DELETE CASCADE,
    minimal_cost FLOAT NOT NULL,
    minimal_eater_reliability VARCHAR(255) NOT NULL,
    is_allowed_before_place_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    is_allowed_for_fast_cancellation BOOLEAN NOT NULL DEFAULT FALSE,
    is_for_vip_only BOOLEAN NOT NULL DEFAULT FALSE
);

