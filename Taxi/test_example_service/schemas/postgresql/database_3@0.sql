DROP SCHEMA IF EXISTS test CASCADE;
CREATE SCHEMA test;

CREATE TABLE test.test_table_3 (
    key TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    up TIMESTAMP,
    number bigint,
    flag boolean DEFAULT FALSE
);
