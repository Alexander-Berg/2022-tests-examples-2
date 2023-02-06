INSERT INTO state.sagas(id, started_at, park_id, driver_id, unique_driver_id,
                        next_mode, next_mode_timepoint, next_mode_settings,
                        prev_mode, prev_mode_timepoint, prev_mode_settings,
                        external_ref, accept_language, compensation_policy, source, change_reason)
VALUES ('1', '2020-05-16', 'parkid1', 'uuid1', 'udi1', 'next_work_mode',
        '2020-04-04 14:00:00+01', '{"rule_id": "next_rule_id"}', 'prev_work_mode', '2020-05-16', '{"rule_id": "prev_rule_id"}',
        'some_unique_key', 'ru', 'allow', 'manual_mode_change', Null ),
       ('2', '2020-05-16', 'parkid2', 'uuid2', 'udi2', 'next_work_mode',
        '2020-04-04 14:00:00+01', '{"rule_id": "next_rule_id"}', 'prev_work_mode', '2020-05-16', '{"rule_id": "prev_rule_id"}',
        'some_unique_key', 'ru', 'allow' , 'manual_mode_change', 'important_reason');

