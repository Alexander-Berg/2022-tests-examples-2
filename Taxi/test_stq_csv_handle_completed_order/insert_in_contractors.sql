INSERT INTO contractor_statistics_view.contractors 
(
    id, 
    unique_driver_id, 
    driver_profile_id, 
    park_id, 
    last_order_id,
    last_order_completion_time,
    onboarding_status,
    is_newbie,
    created_at,
    updated_at
)
VALUES 
    ('72bcbde8-eaed-460f-8f88-eeb4e056c301'::uuid, 'udid1', 'dpid1', 'pid1', 
    NULL, NULL, 'can_be_online', FALSE, '2020-03-08T00:00:00.00Z', '2020-03-08T00:00:00.00Z'),
    ('72bcbde8-eaed-460f-8f88-eeb4e056c302'::uuid, 'udid2', 'dpid2', 'pid2', 
    'order1', '2021-03-08T00:00:00.00Z', 'can_be_online', FALSE, '2020-03-08T00:00:00.00Z', '2020-03-08T00:00:00.00Z');
