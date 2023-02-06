INSERT INTO products.category_groups (id, alias, title_tanker_key, meta, status)
VALUES
('group-1', 'group-1-alias', 'group-1-title-tanker-key', '{ "group-1-meta": "group-1-meta" }', 'active'),
('group-12', 'group-12-alias', 'group-12-title-tanker-key', '{ "group-12-meta": "group-12-meta" }', 'active'),
('group-13', 'group-13-alias', 'group-13-title-tanker-key', '{ "group-13-meta": "group-13-meta" }', 'active'),
('group-2', 'group-2-alias', 'group-2-title-tanker-key', '{ "group-2-meta": "group-2-meta" }', 'active'),
('group-23', 'group-23-alias', 'group-23-title-tanker-key', '{ "group-23-meta": "group-23-meta" }', 'active'),
('group-3', 'group-3-alias', 'group-3-title-tanker-key', '{ "group-3-meta": "group-3-meta" }', 'active')
;

INSERT INTO products.category_groups_images (category_group_id, image_id, image_dimensions)
VALUES
('group-1', 'group-1-image-1', (2, 2)),
('group-1', 'group-1-image-2', (2, 2)),
('group-1', 'group-1-image-3', (2, 2)),
('group-12', 'group-12-image-1', (2, 2)),
('group-12', 'group-12-image-2', (2, 2)),
('group-13', 'group-13-image-1', (2, 2)),
('group-2', 'group-2-image-1', (2, 2)),
('group-2', 'group-2-image-2', (2, 2)),
('group-23', 'group-23-image-1', (2, 2)),
('group-3', 'group-3-image-1', (2, 2)),
('group-3', 'group-3-image-2', (2, 2))
;
