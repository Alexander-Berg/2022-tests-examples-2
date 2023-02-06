INSERT INTO contractor_statistics_view.contractors 
(
    id, 
    unique_driver_id, 
    driver_profile_id, 
    park_id, 
    onboarding_status,
    is_newbie,
    last_online_time,
    updated_at
)
VALUES 
    ('72bcbde8-eaed-460f-8f88-eeb4e056c300'::uuid, 'udid0', 'dpid0', 'pid0', 'can_be_online', FALSE, 
     '2020-03-08T00:00:00.00Z', '2020-03-08T00:00:00.00Z');

INSERT INTO contractor_statistics_view.contractors 
(
    id, 
    unique_driver_id, 
    driver_profile_id, 
    park_id, 
    onboarding_status,
    is_newbie
)
VALUES 
    ('72bcbde8-eaed-460f-8f88-eeb4e056c301'::uuid, 'udid1', 'dpid1', 'pid1', 'can_be_online', FALSE);
