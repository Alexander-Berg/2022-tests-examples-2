GRANT USAGE ON SCHEMA {current_schema} TO taxiro;

GRANT SELECT ON ALL TABLES IN SCHEMA {current_schema} TO taxiro;

INSERT INTO public.ops (schema, op) VALUES ('{current_schema}', 'grants on {current_schema} schema');
