CREATE TABLE foo (
                     id Int32 NOT NULL,
                     value String NOT NULL
) engine = MergeTree() PRIMARY KEY id;
