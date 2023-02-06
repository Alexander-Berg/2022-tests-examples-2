INSERT INTO contractor_statistics_view.triggers 
(
    id, 
    unique_driver_id, 
    park_id, 
    driver_profile_id, 
    trigger_name, 
    counter, 
    trigger_status, 
    created_at, 
    updated_at
)
VALUES 
    /* ожидающие */
    ('c2d29867-3d0b-d497-9191-18a9d8ee7830'::uuid, 'udid1', NULL, NULL, 'skip_chain_order', 2, 'waiting', '2022-03-01 12:00:01', '2022-03-10 14:10:10'),
    ('c2d29867-3d0b-d497-9191-18a9d8ee7831'::uuid, NULL, 'p2', 'd2', 'skip_chain_order', 1, 'waiting', '2022-03-01 10:00:01', '2022-03-15 15:10:10'),
    /* активные */
    ('c2d29867-3d0b-d497-9191-18a9d8ee7832'::uuid, NULL, 'p3', 'd3', 'skip_chain_order', 3, 'active', '2022-03-01 10:00:01', '2022-03-25 18:11:10');
