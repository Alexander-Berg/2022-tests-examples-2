CREATE INDEX CONCURRENTLY i_dummy_bar ON dummy (bar);

INSERT INTO public.ops (schema, op) VALUES ('{current_schema}', 'migration V0003__NONTRANSACTIONAL_Add_index_on_bar_column.sql');
