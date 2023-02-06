-- Default database state

INSERT INTO example_pg.table_with_deletions
(id, some_field, updated_ts, increment, is_deleted)
VALUES
('example_1', 'some_field1', TIMESTAMPTZ('2020-06-22T09:56:00.00Z'), 1, false),
('example_2', 'some_field2', TIMESTAMPTZ('2020-06-23T09:56:00.00Z'), 2, false),
('example_3', 'some_field3', TIMESTAMPTZ('2020-06-23T09:57:00.00Z'), 3, true);
