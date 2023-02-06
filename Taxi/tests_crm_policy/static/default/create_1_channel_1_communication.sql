INSERT INTO crm_policy.entity_types(name) VALUES('user_id') ON CONFLICT(name) DO NOTHING;
INSERT INTO crm_policy.channels (name) VALUES('fullscreen');
INSERT INTO crm_policy.registered_external_communications (campaign_id, experiment_id, expire_time, expected_entity_type_id) VALUES('1', '', ('2020-02-01 14:00:09')::timestamp, 1);

INSERT INTO crm_policy.external_communications_groups (external_communication_id, group_id, relax_time, update_timestamp, channel_id)
	                                                VALUES ((SELECT id from crm_policy.registered_external_communications where campaign_id = '1'), '', '1 sec'::interval, ('2019-02-01 14:00:09')::timestamp, 1);
INSERT INTO crm_policy.round_tables (head) VALUES(0);
