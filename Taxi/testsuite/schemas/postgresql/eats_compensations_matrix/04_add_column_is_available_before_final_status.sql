ALTER TABLE eats_compensations_matrix.situations
    ADD COLUMN IF NOT EXISTS is_available_before_final_status BOOLEAN NOT NULL DEFAULT FALSE;
