CREATE TABLE IF NOT EXISTS public.ops (
    seq SERIAL PRIMARY KEY,
    schema TEXT NOT NULL,
    op TEXT NOT NULL
);

INSERT INTO public.ops (schema, op) VALUES ('{current_schema}', 'beforeAll 00_create_database_ops.sql');
