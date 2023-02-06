INSERT INTO basic_sample_db.main_table(
    key_foo, key_bar, value, updated_ts, key_foo_enum
)
VALUES
('key_pg', 1, 'pg_value_1', '2021-03-21T12:01:00Z', 'key_pg'::basic_sample_db.key_foo_enum_type),
('key_pg', 2, 'pg_value_2', '2021-03-21T12:02:00Z', 'key_pg'::basic_sample_db.key_foo_enum_type);

INSERT INTO basic_sample_db.second_table(
    key_foo, key_bar, second_value
)
VALUES
('key_pg', 1, 'pg_second_value_1');
