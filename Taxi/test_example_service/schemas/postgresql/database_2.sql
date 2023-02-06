DROP SCHEMA IF EXISTS test CASCADE;
CREATE SCHEMA test;

CREATE TABLE test.test_table_2(
    id bigserial PRIMARY KEY,
    content TEXT
);
