START TRANSACTION;

CREATE INDEX
    idx__compensation_matrices__updated_at
    ON eats_compensations_matrix.compensation_matrices
    (updated_at);

CREATE INDEX
    idx__compensation_matrices__created_at
    ON eats_compensations_matrix.compensation_matrices
    (created_at);

CREATE INDEX
    idx__compensation_packs__updated_at
    ON eats_compensations_matrix.compensation_packs
    (updated_at);

CREATE INDEX
    idx__compensation_packs__created_at
    ON eats_compensations_matrix.compensation_packs
    (created_at);

CREATE INDEX
    idx__compensation_types__updated_at
    ON eats_compensations_matrix.compensation_types
    (updated_at);

CREATE INDEX
    idx__compensation_types__created_at
    ON eats_compensations_matrix.compensation_types
    (created_at);

CREATE INDEX
    idx__situation_groups__updated_at
    ON eats_compensations_matrix.situation_groups
    (updated_at);

CREATE INDEX
    idx__situation_groups__created_at
    ON eats_compensations_matrix.situation_groups
    (created_at);

CREATE INDEX
    idx__situations__updated_at
    ON eats_compensations_matrix.situations
    (updated_at);

CREATE INDEX
    idx__situations__created_at
    ON eats_compensations_matrix.situations
    (created_at);

COMMIT;
