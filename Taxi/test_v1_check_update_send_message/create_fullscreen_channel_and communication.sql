INSERT INTO crm_policy.channels (channel_name) VALUES('push');
INSERT INTO crm_policy.communications (communication_name, channel_id, expire_time) VALUES('name_0', 2, NOW() + ('12 hour')::interval);
