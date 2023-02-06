INSERT INTO rt_background_settings
(bp_name, bp_type, bp_settings, bp_enabled)
VALUES
(
'segments_journal',
'claims_journal',
'{"first_instant":0,"host_filter":{"fqdn_host_pattern":"","ctype":"testing_dispatch","host_pattern":""},"period":"100ms","default_employer":"default","bp_description":"","operator_id":"default","freshness":"1m","groupping_attributes":[],"taxi_config_settings":""}',
false
);

INSERT INTO rt_background_settings
(bp_name, bp_type, bp_settings, bp_enabled)
VALUES
(
'propositions_journal',
'propositions_journal',
'{"bp_description":"","groupping_attributes":[],"host_filter":{"fqdn_host_pattern":"","ctype":"testing_dispatch","host_pattern":""},"period":"100ms","freshness":"1m","first_instant":0}',
false
);

INSERT INTO rt_background_settings
(bp_name, bp_type, bp_settings, bp_enabled)
VALUES
(
'p2p_allocation',
'p2p_allocation',
'{"host_filter":{"fqdn_host_pattern":"","ctype":"testing_dispatch","host_pattern":""},"period":"1s","bp_description":"","freshness":"1m","only_pull_dispatch":false,"tariff_areas_filter":"","groupping_attributes":[],"taxi_config_settings":"LOGISTIC_DISPATCHER_P2P_ROBOT_SETTINGS"}',
false
);

INSERT INTO rt_background_settings
(bp_name, bp_type, bp_settings, bp_enabled)
VALUES
(
'p2p_allocation_sadovoe',
'p2p_allocation',
'{"host_filter":{"fqdn_host_pattern":"","ctype":"testing_dispatch","host_pattern":""},"period":"1s","bp_description":"","freshness":"1m","only_pull_dispatch":false,"tariff_areas_filter":"","groupping_attributes":[],"taxi_config_settings":"LOGISTIC_DISPATCHER_P2P_ROBOT_SETTINGS"}',
false
);

INSERT INTO rt_background_settings
(bp_name, bp_type, bp_settings, bp_enabled)
VALUES
(
'p2p_allocation_pd',
'p2p_allocation',
'{"host_filter":{"fqdn_host_pattern":"","ctype":"testing_dispatch","host_pattern":""},"period":"1s","bp_description":"","freshness":"1m","only_pull_dispatch":true,"tariff_areas_filter":"","groupping_attributes":[],"taxi_config_settings":"LOGISTIC_DISPATCHER_P2P_ROBOT_PD"}',
false
);

INSERT INTO rt_background_settings
(bp_name, bp_type, bp_settings, bp_enabled)
VALUES
(
'operator_commands_executor',
'operator_commands_executor',
'{"bp_description":"","groupping_attributes":[],"host_filter":{"fqdn_host_pattern":"","ctype":"testing_dispatch","host_pattern":""},"period":"1s","freshness":"1m","threads_count":1}',
false
);

INSERT INTO rt_background_settings
(bp_name, bp_type, bp_settings, bp_enabled)
VALUES
(
'propositions_notifier',
'propositions_notifier',
'{"bp_description":"","groupping_attributes":[],"host_filter":{"fqdn_host_pattern":"","ctype":"testing_dispatch","host_pattern":""},"period":"1s","freshness":"1m","threads_count":1}',
false
);

INSERT INTO rt_background_settings
(bp_name, bp_type, bp_settings, bp_enabled)
VALUES
(
'employer_factors_watcher',
'employer_factors_watcher',
'{"bp_description":"","kv_storage":"default_cache","groupping_attributes":[],"host_filter":{"fqdn_host_pattern":"","ctype":"testing_dispatch","host_pattern":""},"period":"1s","freshness":"1m","threads_count":1}',
false
);

INSERT INTO rt_background_settings
(bp_name, bp_type, bp_settings, bp_enabled)
VALUES
(
    'state_watcher',
    'state_watcher',
    '{"bp_description":"","kv_storage":"default_cache","groupping_attributes":[],"host_filter":{"fqdn_host_pattern":"","ctype":"testing_dispatch","host_pattern":""},"period":"1s","freshness":"1m","threads_count":1}',
    false
);

INSERT INTO rt_background_settings
(bp_name, bp_type, bp_settings, bp_enabled)
VALUES
(
    'estimation_watcher',
    'estimation_watcher',
    '{"bp_description":"","kv_storage":"default_cache","groupping_attributes":[],"host_filter":{"fqdn_host_pattern":"","ctype":"testing_dispatch","host_pattern":""},"period":"1s","freshness":"1m","threads_count":1}',
    false
);

INSERT INTO employers (employer_code, employer_type) VALUES ('default', 'default');
INSERT INTO employers (employer_code, employer_type) VALUES ('eats', 'eats');
INSERT INTO employers (employer_code, employer_type) VALUES ('food_retail', 'food_retail');
INSERT INTO employers (employer_code, employer_type) VALUES ('grocery', 'grocery');
