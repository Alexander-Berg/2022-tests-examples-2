ALTER TABLE dummy ADD COLUMN alternate_colour dummy.rainbow NOT NULL DEFAULT 'red';

INSERT INTO public.ops (schema, op) VALUES ('{current_schema}', 'migration V0002__Add_baz_column_to_foo.sql');
