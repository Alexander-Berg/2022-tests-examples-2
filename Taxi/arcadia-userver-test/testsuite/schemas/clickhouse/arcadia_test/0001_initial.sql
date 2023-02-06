CREATE TABLE test_values (
                     id String NOT NULL,
                     value String NOT NULL
) engine = MergeTree() PRIMARY KEY id;
