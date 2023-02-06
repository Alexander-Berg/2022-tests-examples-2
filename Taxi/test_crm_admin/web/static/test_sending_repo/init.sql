INSERT INTO crm_admin.segment
    (id, yql_shared_url, yt_table, control, created_at)
VALUES (2, '', '', 1, NOW());

INSERT INTO crm_admin.group
    (id, segment_id, params, created_at, updated_at)
VALUES (2, 2, '{}', NOW(), NOW());
