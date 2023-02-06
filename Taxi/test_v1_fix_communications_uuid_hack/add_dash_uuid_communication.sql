insert into crm_policy.registered_external_communications(campaign_id, expire_time) VALUES('8a457abd-c10d-4450-a3ab-199f43ed44bc', NOW() + '1000 hours'::interval);
insert into crm_policy.external_communications_groups(external_communication_id, relax_time, group_id, update_timestamp, channel_id)
    VALUES((SELECT id from crm_policy.registered_external_communications where campaign_id = '8a457abd-c10d-4450-a3ab-199f43ed44bc')
    , '1 hour'::interval, '__default__', NOW(),2);
