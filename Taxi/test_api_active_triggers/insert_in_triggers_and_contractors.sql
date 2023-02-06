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
    ('72bcbde8-eaed-460f-8f88-eeb4e056c301'::uuid, 'udid1', 'dpid1', 'pid1', 'can_be_online', FALSE),
    ('72bcbde8-eaed-460f-8f88-eeb4e056c302'::uuid, 'udid2', 'dpid2', 'pid2', 'can_be_online', FALSE),
    ('72bcbde8-eaed-460f-8f88-eeb4e056c303'::uuid, 'udid3', 'dpid3', 'pid3', 'can_be_online', FALSE),
    ('72bcbde8-eaed-460f-8f88-eeb4e056c304'::uuid, 'udid5', 'dpid5', 'pid5', 'can_be_online', FALSE);

INSERT INTO contractor_statistics_view.triggers 
(
    id, 
    unique_driver_id, 
    driver_profile_id, 
    park_id, 
    trigger_name, 
    trigger_status
)
VALUES 
    ('c2d29867-3d0b-d497-9191-18a9d8ee7830'::uuid, NULL, 'dpid1', 'pid1', 'trigger1', 'active'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7831'::uuid, NULL, 'dpid1', 'invalid_pid1', 'trigger2', 'active'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7832'::uuid, NULL, 'dpid1', 'pid1', 'trigger3', 'waiting'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7833'::uuid, 'udid1', NULL, NULL, 'trigger8', 'active'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7834'::uuid, NULL, 'invalid_dpid2', 'pid2', 'trigger4', 'active'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7835'::uuid, 'udid4', NULL, NULL, 'trigger5', 'active'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7836'::uuid, 'udid5', NULL, NULL, 'trigger6', 'waiting'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7837'::uuid, NULL, 'dpid5', 'pid5', 'trigger7', 'active');
