INSERT INTO crm_policy.entity_types(name) VALUES('user_id') ON CONFLICT(name) DO NOTHING;
INSERT INTO crm_policy.registered_external_communications (campaign_id, experiment_id, expire_time)
                                VALUES('8a457abd-c10d-4450-a3ab-199f43ed44bc', '', NOW() + ('12 hour')::interval);
INSERT INTO crm_policy.external_communications_groups (external_communication_id, group_id, relax_time, update_timestamp, channel_id)
	                                                VALUES ((SELECT id from crm_policy.registered_external_communications
	                                                    where campaign_id = '8a457abd-c10d-4450-a3ab-199f43ed44bc'), '', '1 sec'::interval, ('2019-02-01 14:00:09')::timestamp,2)