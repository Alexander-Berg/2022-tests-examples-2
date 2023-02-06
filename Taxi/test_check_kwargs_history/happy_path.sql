-- is_broken fill NULL automatically

INSERT INTO clients_schema.consumer_kwargs_history
    (consumer, history, updation_time)
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
        )
;
