UPDATE eats_compensations_matrix.situations
    SET is_available_before_final_status = TRUE
    WHERE group_id = 1 OR group_id = 16; -- long delivery waiting (1) or long restaurant waiting (16)
