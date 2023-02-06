INSERT INTO clients_schema.experiments
    (id, name, date_from, date_to, rev, clauses, predicate, description, enabled, schema, closed, is_technical)
        VALUES
            (
                1,
                'check_map_style',
                '2020-05-13T04:06:47+0300',
                '2020-05-13T04:06:47+0300',
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                'DESCRIPTION',
                TRUE,
                '',
                FALSE,
                NULL);
