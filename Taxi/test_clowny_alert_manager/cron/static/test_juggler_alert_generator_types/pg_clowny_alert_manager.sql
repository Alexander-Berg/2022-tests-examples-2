INSERT INTO alert_manager.juggler_host
    (juggler_host)
VALUES
    ('some_host'),
    ('pg_taxi-infra_clownductor_stable')
;

INSERT INTO alert_manager.branch_juggler_host
    (clown_branch_id, juggler_host_id)
VALUES
    (1, 1),
    (10, 1),
    (2, 2)
;
