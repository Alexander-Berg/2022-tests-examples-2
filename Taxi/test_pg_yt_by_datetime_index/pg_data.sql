INSERT INTO basic_sample_db.main_table(
    key_foo, key_bar, value, updated_ts
)
VALUES
('key_common', 0, 'pg_value_1', '2021-03-21T12:01:00Z'),
('key_common', 1, 'pg_value_2', '2021-03-21T12:02:00Z');

INSERT INTO basic_sample_db.second_table(
    key_foo, key_bar, second_value
)
VALUES
('key_common', 0, 'pg_second_value_1');
