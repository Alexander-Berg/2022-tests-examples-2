INSERT INTO eats_partners.last_activity (partner_id, last_activity_at, created_at)
VALUES
       (1, NOW(), NOW()),
       (2, NOW() - INTERVAL '12 HOURS', NOW()),
       (3, NOW() - INTERVAL '23 HOURS', NOW()),
       (4, NOW() - INTERVAL '30 SECONDS', NOW()),
       (5, NOW() - INTERVAL '2 DAYS', NOW());
