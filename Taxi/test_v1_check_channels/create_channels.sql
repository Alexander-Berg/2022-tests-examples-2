INSERT INTO crm_policy.entity_types(name) VALUES('user_id') ON CONFLICT(name) DO NOTHING;

INSERT INTO crm_policy.channels (name) VALUES('fullscreen') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_policy.channels (name) VALUES('push') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_policy.channels (name) VALUES('sms') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_policy.channels (name) VALUES('wall') ON CONFLICT (name) DO NOTHING;

INSERT INTO crm_policy.channels (name) VALUES('promo_fs') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_policy.channels (name) VALUES('promo_card') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_policy.channels (name) VALUES('promo_notification') ON CONFLICT (name) DO NOTHING;
INSERT INTO crm_policy.channels (name) VALUES('new_unhandled_channel') ON CONFLICT (name) DO NOTHING;

INSERT INTO crm_policy.round_tables (head) VALUES(0);

INSERT INTO crm_policy.registered_external_communications (campaign_id, experiment_id, expire_time, expected_entity_type_id) VALUES('fullscreen', '', NOW() + ('12 hour')::interval, 1);
INSERT INTO crm_policy.registered_external_communications (campaign_id, experiment_id, expire_time, expected_entity_type_id) VALUES('push', '', NOW() + ('12 hour')::interval, 1);
INSERT INTO crm_policy.registered_external_communications (campaign_id, experiment_id, expire_time, expected_entity_type_id) VALUES('sms', '', NOW() + ('12 hour')::interval, 1);
INSERT INTO crm_policy.registered_external_communications (campaign_id, experiment_id, expire_time, expected_entity_type_id) VALUES('wall', '', NOW() + ('12 hour')::interval, 1);
INSERT INTO crm_policy.registered_external_communications (campaign_id, experiment_id, expire_time, expected_entity_type_id) VALUES('promo_fs', '', NOW() + ('12 hour')::interval, 1);
INSERT INTO crm_policy.registered_external_communications (campaign_id, experiment_id, expire_time, expected_entity_type_id) VALUES('promo_card', '', NOW() + ('12 hour')::interval, 1);
INSERT INTO crm_policy.registered_external_communications (campaign_id, experiment_id, expire_time, expected_entity_type_id) VALUES('promo_notification', '', NOW() + ('12 hour')::interval, 1);

INSERT INTO crm_policy.external_communications_groups (external_communication_id, group_id, relax_time, update_timestamp, channel_id)
	                                                VALUES ((SELECT id from crm_policy.registered_external_communications where campaign_id = 'fullscreen'), '', '1 sec'::interval, ('2019-02-01 14:00:09')::timestamp, 1);

INSERT INTO crm_policy.external_communications_groups (external_communication_id, group_id, relax_time, update_timestamp, channel_id)
	                                                VALUES ((SELECT id from crm_policy.registered_external_communications where campaign_id = 'push'), '', '1 sec'::interval, ('2019-02-01 14:00:09')::timestamp,2);

INSERT INTO crm_policy.external_communications_groups (external_communication_id, group_id, relax_time, update_timestamp, channel_id)
	                                                VALUES ((SELECT id from crm_policy.registered_external_communications where campaign_id = 'sms'), '', '1 sec'::interval, ('2019-02-01 14:00:09')::timestamp,3);

INSERT INTO crm_policy.external_communications_groups (external_communication_id, group_id, relax_time, update_timestamp, channel_id)
	                                                VALUES ((SELECT id from crm_policy.registered_external_communications where campaign_id = 'wall'), '', '1 sec'::interval, ('2019-02-01 14:00:09')::timestamp,4);

INSERT INTO crm_policy.external_communications_groups (external_communication_id, group_id, relax_time, update_timestamp, channel_id)
	                                                VALUES ((SELECT id from crm_policy.registered_external_communications where campaign_id = 'promo_fs'), '', '1 sec'::interval, ('2019-02-01 14:00:09')::timestamp,5);

INSERT INTO crm_policy.external_communications_groups (external_communication_id, group_id, relax_time, update_timestamp, channel_id)
	                                                VALUES ((SELECT id from crm_policy.registered_external_communications where campaign_id = 'promo_card'), '', '1 sec'::interval, ('2019-02-01 14:00:09')::timestamp,6);

INSERT INTO crm_policy.external_communications_groups (external_communication_id, group_id, relax_time, update_timestamp, channel_id)
	                                                VALUES ((SELECT id from crm_policy.registered_external_communications where campaign_id = 'promo_notification'), '', '1 sec'::interval, ('2019-02-01 14:00:09')::timestamp,7);

