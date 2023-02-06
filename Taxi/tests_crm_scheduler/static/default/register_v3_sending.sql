INSERT INTO crm_scheduler.sendings (campaign_id, group_id, policy_enabled, send_enabled, channel_id, size, dependency_uuid, priority_id,
                                    sending_id, generation_version, steps)
                                    VALUES(
                                            'company_id_1', '1_testing', False, False, -1, 123, '8430b07a-0032-11ec-9a03-0242ac130003'
                                            , 2, '7d27b35a-0032-11ec-9a03-0242ac130003', 3,'{crm_policy,eda_push,driver_wall,logs}'
                                          );
