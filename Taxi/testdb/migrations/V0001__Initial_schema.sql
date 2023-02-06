/* pgmigrate-encoding: utf-8 */

CREATE TABLE dummy (
    id BIGINT PRIMARY KEY,
    bar dummy.test_type NOT NULL
);

CREATE TABLE some_data(
    id BIGSERIAL PRIMARY KEY,
    data text NOT NULL
);

INSERT INTO some_data(data) VALUES ('UTF-8: ᚱᚨᚷᚾᚨᚱᛟᚲ');

INSERT INTO public.ops (schema, op) VALUES ('{current_schema}', 'migration V0001__Initial_schema_foo.sql');
