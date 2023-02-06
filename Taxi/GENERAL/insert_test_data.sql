insert into test_data (description, schema_id, start_time, precedent_time,
                       end_time, data, meta)
       values ($1, $2, $3, $4, $5, $6, $7)
       returning test_id

