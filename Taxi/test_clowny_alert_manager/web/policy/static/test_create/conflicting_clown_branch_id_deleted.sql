INSERT INTO alert_manager.juggler_host
    (juggler_host)
VALUES
    ('some_other_direct_link')
;

INSERT INTO alert_manager.branch_juggler_host
    (clown_branch_id, juggler_host_id, deleted_at)
VALUES
    (777, 1, NOW())
;
