select id, description, test_data_id, schema_id, out_point_id,
       start_time, end_time, check_type, check_params, is_enabled
from test_cases
where id in (select * from unnest($1));
