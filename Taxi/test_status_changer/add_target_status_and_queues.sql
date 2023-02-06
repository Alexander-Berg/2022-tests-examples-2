INSERT INTO callcenter_queues.target_status
(
    sip_username,
    status,
    project,
    updated_seq
)
 VALUES
('a', 'connected', 'disp', 1);

INSERT INTO callcenter_queues.target_queues
(
    sip_username,
    metaqueues,
    updated_seq
)
VALUES
    ('a', '{ru_taxi_disp}'::VARCHAR[], 1),
    ('b', '{ru_taxi_disp}'::VARCHAR[], 2);

UPDATE callcenter_queues.changes_positions SET
status_changes_position = 0,
queues_changes_position = 0
WHERE consumer = 'status_changer';
