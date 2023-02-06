INSERT INTO clients_schema.experiments
    (id, name, date_from, date_to, rev, clauses, predicate, description, enabled, schema, closed)
        VALUES
            (
                1,
                'existed_experiment',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                ('{"type": "in_set", "init": {'
                || '"set": ["aaaabbbcdd"], '
                || '"set_elem_type": "string", '
                || '"transform": "replace_phone_to_phone_id", '
                || '"phone_type": "yandex", '
                || '"arg_name": "phone_id"'
                || '}}')::jsonb,
                'DESCRIPTION',
                TRUE,
                '',
                FALSE);
