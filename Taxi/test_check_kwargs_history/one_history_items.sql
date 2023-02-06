-- is_broken fill NULL automatically

INSERT INTO clients_schema.consumer_kwargs_history
    (consumer, history, updation_time)
    VALUES
        (
            'test_consumer',
            jsonb_build_object(
                'kwargs', '[]'::jsonb,
                'metadata', '{}'::jsonb,
                'library_version', '1',
                'updated', CURRENT_TIMESTAMP
            ),
            CURRENT_TIMESTAMP
        )
        ,(
            'test_consumer2',
            jsonb_build_object(
                'kwargs', '[]'::jsonb,
                'metadata', '{}'::jsonb,
                'library_version', '1',
                'updated', CURRENT_TIMESTAMP
            ),
            CURRENT_TIMESTAMP
        )
        ,(
            'test_consumer3',
            jsonb_build_object(
                'kwargs', '[]'::jsonb,
                'metadata', '{}'::jsonb,
                'library_version', '1',
                'updated', CURRENT_TIMESTAMP
            ),
            CURRENT_TIMESTAMP
        )
        ,(
            'test_consumer4',
            jsonb_build_object(
                'kwargs', '[]'::jsonb,
                'metadata', '{}'::jsonb,
                'library_version', '1',
                'updated', CURRENT_TIMESTAMP
            ),
            CURRENT_TIMESTAMP
        )
;
