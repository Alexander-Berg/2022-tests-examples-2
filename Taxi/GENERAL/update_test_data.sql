update test_data
set description=$2, schema_id=$3, start_time=$4,
    precedent_time=$5, end_time=$6, data=$7, meta=$8
where test_id=$1;
