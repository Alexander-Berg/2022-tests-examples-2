INSERT INTO clients_schema.experiments (id, name, rev, is_config, date_from, date_to)
    VALUES
        (723, 'experiment_with_revisions', 254570, False,
            '2020-01-01'::timestamp, '2020-01-01'::timestamp)
;
INSERT INTO clients_schema.revision_history (experiment_id, rev)
    VALUES
        (723, 253445),
        (723, 253584),
        (723, 253732),
        (723, 253877),
        (723, 254021),
        (723, 254164),
        (723, 254300),
        (723, 254435),
        (723, 254570)
;
