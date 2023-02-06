INSERT INTO contractor_statistics_view.contractors 
(
    id, 
    unique_driver_id, 
    driver_profile_id, 
    park_id, 
    onboarding_status,
    is_newbie,
    updated_at
)
VALUES 
    ('72bcbde8-eaed-460f-8f88-eeb4e056c301'::uuid, 'udid1', 'dpid1', 'pid1', 'can_be_online', FALSE, '2020-03-08T00:00:00.00Z'),
    ('72bcbde8-eaed-460f-8f88-eeb4e056c302'::uuid, 'udid2', 'dpid2_0', 'pid2_0', 'can_be_online', FALSE, '2020-03-08T00:00:00.00Z'),
    ('72bcbde8-eaed-460f-8f88-eeb4e056c303'::uuid, 'udid2', 'dpid2_1', 'pid2_1', 'can_be_online', FALSE, '2020-03-08T00:00:00.00Z'),
    ('72bcbde8-eaed-460f-8f88-eeb4e056c304'::uuid, 'udid3', 'dpid3_0', 'pid3_0', 'can_be_online', FALSE, '2020-03-08T00:00:00.00Z'),
    ('72bcbde8-eaed-460f-8f88-eeb4e056c305'::uuid, 'udid3', 'dpid3_1', 'pid3_1', 'can_be_online', FALSE, '2020-03-08T00:00:00.00Z'),
    ('72bcbde8-eaed-460f-8f88-eeb4e056c306'::uuid, 'udid4', 'dpid4', 'pid4', 'can_be_online', FALSE, '2020-03-08T00:00:00.00Z'),
    ('72bcbde8-eaed-460f-8f88-eeb4e056c307'::uuid, 'udid9', 'dpid90', 'pid90', 'can_be_online', FALSE, '2020-03-08T00:00:00.00Z'),
    ('72bcbde8-eaed-460f-8f88-eeb4e056c308'::uuid, 'udid9', 'dpid91', 'pid91', 'can_be_online', FALSE, '2020-03-08T00:00:00.00Z'),
    ('72bcbde8-eaed-460f-8f88-eeb4e056c309'::uuid, 'udid9', 'dpid94', 'pid94', 'can_be_online', FALSE, '2020-03-08T00:00:00.00Z'),
    ('72bcbde8-eaed-460f-8f88-eeb4e056c310'::uuid, 'invalid_udid9', 'invalid_dpid95', 'pid95', 'can_be_online', FALSE, '2020-03-08T00:00:00.00Z');


INSERT INTO contractor_statistics_view.triggers 
(
    id, 
    unique_driver_id, 
    driver_profile_id, 
    park_id, 
    trigger_name, 
    counter, 
    trigger_status,
    created_at,
    updated_at
)
VALUES 
    ('c2d29867-3d0b-d497-9191-18a9d8ee7831'::uuid, 'udid1', NULL, NULL, 'trigger02', 1, 'active',
    '2020-03-08T00:00:00.00Z', '2020-03-08T00:00:00.00Z'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7832'::uuid, 'udid1', NULL, NULL, 'trigger03', 2, 'waiting',
    '2020-03-08T00:00:00.00Z', '2020-03-08T00:00:00.00Z'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7833'::uuid, NULL, 'dpid2', 'pid2', 'trigger04', 3, 'active',
    '2020-03-08T00:00:00.00Z', '2020-03-08T00:00:00.00Z'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7834'::uuid, 'udid2', NULL, NULL, 'trigger05', 4, 'active',
    '2020-03-08T00:00:00.00Z', '2020-03-08T00:00:00.00Z'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7835'::uuid, 'udid2', NULL, NULL, 'trigger06', 5, 'waiting',
    '2020-03-08T00:00:00.00Z', '2020-03-08T00:00:00.00Z'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7836'::uuid, 'udid3', NULL, NULL, 'trigger07', 1, 'active',
    '2020-03-08T00:00:00.00Z', '2020-03-08T00:00:00.00Z'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7837'::uuid, 'udid3', NULL, NULL, 'trigger08', 3, 'active',
    '2020-03-08T00:00:00.00Z', '2020-03-08T00:00:00.00Z'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7838'::uuid, 'udid3', NULL, NULL, 'trigger09', 4, 'active',
    '2020-03-08T00:00:00.00Z', '2020-03-08T00:00:00.00Z'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7839'::uuid, 'udid3', NULL, NULL, 'trigger11', 5, 'waiting',
    '2020-03-08T00:00:00.00Z', '2020-03-08T00:00:00.00Z'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7840'::uuid, 'udid4', NULL, NULL, 'trigger10', 5, 'waiting',
    '2020-03-08T00:00:00.00Z', '2020-03-08T00:00:00.00Z'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7841'::uuid, 'udid4', NULL, NULL, 'trigger08', 2, 'waiting',
    '2020-03-08T00:00:00.00Z', '2020-03-08T00:00:00.00Z'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7842'::uuid, 'udid4', NULL, NULL, 'trigger09', 5, 'waiting',
    '2020-03-08T00:00:00.00Z', '2020-03-08T00:00:00.00Z'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7843'::uuid, 'udid4', NULL, NULL, 'trigger11', 4, 'active',
    '2020-03-08T00:00:00.00Z', '2020-03-08T00:00:00.00Z');
