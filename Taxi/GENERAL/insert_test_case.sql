insert into test_cases
    (description, test_data_id, schema_id, out_point_id,
    start_time, end_time, check_type, check_params, is_enabled
    ) values ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    returning id;
