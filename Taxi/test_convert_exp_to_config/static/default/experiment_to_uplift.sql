INSERT INTO clients_schema.consumers (name) VALUES ('test_consumer');
INSERT INTO clients_schema.applications (name) VALUES ('android');


-- experiment with apps
INSERT INTO clients_schema.experiments (id, name, date_from, date_to,
                                        enabled,
                                        closed,
                                        rev,
                                        default_value,
                                        clauses,
                                        predicate,
                                        description,
                                        schema)
    VALUES (5, 'experiment_to_uplift', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
        TRUE,
        FALSE,
        nextval('clients_schema.clients_rev'),
        'null',
        '[{"title": "clause_title", "value": {}, "predicate": {"type": "true"}, "extension_method": "extend"}]'::jsonb,
        '{"type": "true"}'::jsonb,
        'Experiment with apps',
        '
type: object
additionalProperties: false
required:
  - type
properties:
    type:
        type: string');

INSERT INTO clients_schema.owners (experiment_id, owner_login)
    VALUES (5, 'serg-novikov')
;

INSERT INTO clients_schema.watchers (experiment_id, watcher_login, last_revision)
    VALUES (5, 'serg-novikov', 1)
;

INSERT INTO clients_schema.fallbacks (
        id,
        short_description,
        what_happens_when_turn_off,
        need_turn_off,
        placeholder
    )
    VALUES (5, 'Description', 'what_happens_when_turn_off', TRUE, 'placeholder')
;

INSERT INTO clients_schema.experiments_applications (
        experiment_id,
        application_id,
        version_from,
        version_to
    )
    VALUES (5, 1, '0.0.0', '10.0.10')
;

INSERT INTO clients_schema.experiments_consumers (
        experiment_id, consumer_id, merge_tag
    )
    VALUES (5, 1, 'merge_tag')
;
