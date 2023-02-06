INSERT INTO clients_schema.experiments
    (id, name, date_from, date_to, rev, clauses, predicate, description, enabled, schema, closed, self_ok, department)
    VALUES
    (
        1,
        'check_map_style',
        '2000-01-01T00:00:00',
        '2100-01-01T00:00:00',
        nextval('clients_schema.clients_rev'),
        '[{"title": "default", "predicate": {"type": "true"}, "value": {}}]'::jsonb,
        '{"type": "true"}'::jsonb,
        'DESCRIPTION',
        TRUE,
        E'\ndescription: ''default schema''\nadditionalProperties: true\n    ',
        FALSE,
        FALSE,
        'common'
    )
;

INSERT INTO clients_schema.experiments_consumers
    (experiment_id, consumer_id)
    VALUES
    (1, 1) -- check_map_style, test_consumer
;
