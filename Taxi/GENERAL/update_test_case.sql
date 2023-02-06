update test_cases
set
    description=$2, test_data_id=$3, schema_id=$4,
    out_point_id=$5, start_time=$6, end_time=$7,
    check_type=$8, check_params=$9, is_enabled=$10
where id=$1;
