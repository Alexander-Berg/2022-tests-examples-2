CREATE DATABASE test;

CREATE TABLE test.test_table_3parts (
    col Date
)
ENGINE = MergeTree()
PARTITION BY col
ORDER BY col
SETTINGS index_granularity = 8192;

CREATE TABLE test.test_table_6parts (
    col Date
)
ENGINE = MergeTree()
PARTITION BY col
ORDER BY col
SETTINGS index_granularity = 8192;

CREATE TABLE test.test_empty_table (
    col Date
)
ENGINE = MergeTree()
PARTITION BY col
ORDER BY col
SETTINGS index_granularity = 8192;
