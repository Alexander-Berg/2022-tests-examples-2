select test_id, description, schema_id, start_time, precedent_time,
        end_time, data, meta
from test_data
where test_id=$1;
