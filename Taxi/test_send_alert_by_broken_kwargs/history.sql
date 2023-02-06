-- ✔ clients_schema.consumer_kwargs_history
-- ✔ clients_schema.consumers
-- ✔ clients_schema.experiments_consumers
-- ✔ clients_schema.experiments
-- ✔ clients_schema.owners


INSERT INTO clients_schema.consumers (id, name) VALUES (1, 'test_consumer'), (2, 'test_consumer2'), (3, 'test_consumer3');

INSERT INTO clients_schema.experiments
    (id, name, date_from, date_to, rev, clauses, predicate, description, enabled, schema)
        VALUES
            (1, 'first', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, '')
            ,(2, 'second', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, '')
            ,(3, 'third', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, '')
            ,(4, 'four', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, '')
            ,(5, 'fifth', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, nextval('clients_schema.clients_rev'), '[]'::jsonb, '{"type": "true"}'::jsonb, 'DESCRIPTION', TRUE, '')
;

INSERT INTO clients_schema.experiments_consumers (experiment_id, consumer_id)
    VALUES
        (1, 1)
        ,(2, 1)
        ,(2, 2)
        ,(3, 1)
        ,(3, 2)
        ,(3, 3)
        ,(4, 1)
        ,(4, 3)
        ,(5, 3)
;

INSERT INTO clients_schema.owners (owner_login, experiment_id)
    VALUES
        ('owner_1', 1)
        ,('owner_1', 2)
        ,('owner_2', 2)
        ,('owner_1', 3)
        ,('owner_2', 4)
;


INSERT INTO clients_schema.consumer_kwargs_history
    (consumer, history, updation_time, is_broken)
    VALUES
        (
            'test_consumer'
            ,jsonb_build_object(
                                'kwargs', '[]'::jsonb
                                ,'metadata', '{}'::jsonb
                                ,'library_version', '1'
                                ,'updated', '2019-01-09T12:00:00'::timestamptz
                            )
            ,'2019-01-09T12:00:00'::timestamptz
            , FALSE
        )
        ,(
            'test_consumer'
            ,jsonb_build_object(
                            'kwargs', '[{"name": "phone_id", "type": "string", "is_mandatory": false}]'::jsonb
                            ,'metadata', '{}'::jsonb
                            ,'library_version', '2-non-broken'
                            ,'updated', '2019-01-09T13:00:00'::timestamptz
                        )
            ,'2019-01-09T13:00:00'::timestamptz
            , FALSE
        )
        ,(
            'test_consumer'
            ,jsonb_build_object(
                            'kwargs', '[{"name": "phone_id", "type": "datetime", "is_mandatory": false}]'::jsonb
                            ,'metadata', '{}'::jsonb
                            ,'library_version', '3-broken'
                            ,'updated', '2019-01-09T14:00:00'::timestamptz
                        )
            ,'2019-01-09T14:00:00'::timestamptz
            , TRUE
        )
        ,(
            'test_consumer'
            ,jsonb_build_object(
                            'kwargs', '[]'::jsonb
                            ,'metadata', '{}'::jsonb
                            ,'library_version', '4-broken'
                            ,'updated', '2019-01-09T15:00:00'::timestamptz
                        )
            ,'2019-01-09T15:00:00'::timestamptz
            , TRUE
        )
;
