-- add experiments
INSERT INTO clients_schema.experiments
    (name, date_from, date_to, rev, clauses, predicate, description, schema, enabled, closed, is_config, department)
        VALUES
            ( -- id 1
                'blacklisted_phones',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                'DESCRIPTION',
                '',
                TRUE, FALSE, FALSE,
                'commando'
            ),( -- id 2
                'country_merchant_ids',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                'DESCRIPTION',
                '',
                TRUE, FALSE, FALSE,
                NULL
            ),( -- id 3
                'default_toll_roads_usage',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                'DESCRIPTION',
                '',
                TRUE, FALSE, FALSE,
                NULL
            ),( -- id 4
                'shortcuts_ranking_timetable',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                'DESCRIPTION',
                '',
                TRUE, FALSE, TRUE,
                NULL
            ),( -- id 5
                'no_fallback',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                'DESCRIPTION - no fallback',
                '',
                TRUE, FALSE, FALSE,
                NULL
            ),( -- id 6
                'no_placeholder',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                nextval('clients_schema.clients_rev'),
                '[]'::jsonb,
                '{"type": "true"}'::jsonb,
                'DESCRIPTION - no placeholder',
                '',
                TRUE, FALSE, FALSE,
                NULL
            )
;

-- link to consumers
INSERT INTO clients_schema.experiments_consumers
    (experiment_id, consumer_id)
    VALUES
        (3, 1),
        (3, 2),
        (2, 2),
        (1, 3),
        (4, 4),
        (5, 5),
        (6, 5)
;

-- link to onwers
INSERT INTO clients_schema.owners
    (experiment_id, owner_login)
    VALUES
        (3, 'serg-novikov'),
        (3, 'dvasiliev')
;

-- make link to fallback
INSERT INTO clients_schema.fallbacks
    (id, short_description, what_happens_when_turn_off, placeholder, need_turn_off)
    VALUES
        (
            1,
            'Short description',
            'Blackout',
            'link',
            TRUE),
        (
            2,
            'Blah-Blah',
            'Crash',
            'link',
            FALSE),
        (
            3,
            'Nothing',
            'Nothing',
            'link',
            FALSE),
        (
            4,
            'Nothing',
            'Nothing',
            'link',
            TRUE),
        (
            6,
            'Nothing',
            'Nothing',
            NULL,
            TRUE)
;
