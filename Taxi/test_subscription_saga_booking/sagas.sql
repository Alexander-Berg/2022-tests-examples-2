INSERT INTO state.sagas(id, started_at, park_id, driver_id, unique_driver_id,
                        next_mode, next_mode_timepoint, next_mode_settings,
                        prev_mode, prev_mode_timepoint, prev_mode_settings,
                        external_ref, accept_language, compensation_policy, source, context)
-- Init context to satisfy booking with slot_policy contractor_tariff_zone
VALUES ('1', '2020-05-16', 'parkid1', 'uuid1', 'udi1', 'next_work_mode',
        '2020-04-04 14:00:00+01', '{"rule_id":"next_rule_id", "shift_close_time": "00:01"}', 'prev_work_mode', '2020-04-02 13:00:00+01', '{"rule_id":"prev_rule_id", "shift_close_time": "00:01"}',
        'some_unique_key', 'ru', 'allow', 'manual_mode_change', '{"prev_mode": {}, "next_mode": {"tariff_zone": "next_context_zone"}}'),
       ('2', '2020-05-16', 'parkid2', 'uuid2', 'udi2', 'next_work_mode',
        '2020-04-04 14:00:00+01', '{"rule_id":"next_rule_id", "shift_close_time": "00:01"}', 'prev_work_mode', '2020-04-02 13:00:00+01', '{"rule_id":"prev_rule_id", "shift_close_time": "00:01"}',
        'some_unique_key', 'ru', 'allow', 'manual_mode_change', null),
       ('3', '2020-05-16', 'parkid3', 'uuid3', 'udi3', 'prev_work_mode',
        '2020-04-04 14:00:00+01', '{"rule_id":"next_rule_id", "shift_close_time": "00:01"}', 'prev_work_mode', '2020-04-02 13:00:00+01', '{"rule_id":"prev_rule_id", "shift_close_time": "00:01"}',
        'some_unique_key', 'ru', 'allow', 'service_mode_change', null),
       ('7', '2020-05-16', 'parkid7', 'uuid7', 'udi7', 'next_work_mode',
        '2020-04-04 14:00:00+01', '{"rule_id":"next_rule_id", "shift_close_time": "00:01"}', 'prev_work_mode', '2020-04-02 13:00:00+01', '{"rule_id":"prev_rule_id", "shift_close_time": "00:01"}',
        'some_unique_key', 'ru', 'allow', 'service_mode_change', '{"prev_mode": {}, "next_mode": {"tariff_zone": "next_context_zone"}}');

