INSERT INTO alert_manager.juggler_host
    (juggler_host)
VALUES
    ('some_direct_link'),
    ('some_pg_direct_link'),
    ('some_direct_link2')
;

INSERT INTO alert_manager.branch_juggler_host
    (clown_branch_id, juggler_host_id)
VALUES
    (777, 1),
    (555, 2),
    (444, 3)
;
