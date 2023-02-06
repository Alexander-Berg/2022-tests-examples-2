-- Default database state

INSERT INTO example_pg.table
    (id, some_field, updated_ts, increment)
VALUES
    ('example_1', 'some_field1', TIMESTAMPTZ('2020-06-22T09:56:00.00Z'), 1),
    ('example_2', 'some_field2', TIMESTAMPTZ('2020-06-23T09:56:00.00Z'), 2);
