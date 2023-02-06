INSERT INTO gp.uptime (database_name, update_dttm)
select 'ritchie',
       generate_series(current_date - interval '1 day', current_date - interval '1 millisecond', '1 minute')
