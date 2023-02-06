ALTER TYPE rainbow ADD VALUE IF NOT EXISTS 'white' BEFORE 'red';
ALTER TYPE rainbow ADD VALUE IF NOT EXISTS 'black' AFTER 'violet';

ALTER TYPE test_type ADD ATTRIBUTE ts TIMESTAMPTZ;

INSERT INTO public.ops (schema, op) VALUES ('{current_schema}', 'migration V0003__NONTRANSACTIONAL_Add_some_colors.sql');
