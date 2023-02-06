INSERT INTO eats_restapp_communications.feedbacks
    (partner_id, slug, score, comment, created_at)
VALUES
    (42, 'dashboard', 2, 'comment_old', '2021-12-01T12:00:00'::timestamptz),
    (42, 'dashboard', 5, 'comment_new', '2022-02-01T12:00:00'::timestamptz),
    (42, 'orders', 4, NULL, '2022-02-01T12:00:00'::timestamptz);
