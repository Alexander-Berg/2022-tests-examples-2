select id, description, schema_id, check_type, is_enabled
from test_cases
where schema_id=$1
order by id desc;
