INSERT INTO eats_order_revision.revisions (id, created_at)
VALUES (2, '2022-02-02T22:00:00'::timestamptz);

INSERT INTO eats_order_revision.revision_tags (id, revision_id, created_at)
VALUES (2, 2, '2022-02-02T22:00:00'::timestamptz);
