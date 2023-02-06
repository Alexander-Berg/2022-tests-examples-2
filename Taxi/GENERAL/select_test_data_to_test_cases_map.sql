select test_data_id, array_agg(id) test_cases
from test_cases
group by test_data_id
order by test_data_id;
