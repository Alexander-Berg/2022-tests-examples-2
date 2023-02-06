INSERT INTO products.layouts (id, alias, meta, status)
VALUES
('layout-1', 'layout-alias-5', '{ "meta-5": "meta-5" }', 'active'),
('layout-2', 'layout-alias-6', '{ "meta-6": "meta-6" }', 'active')
;

INSERT INTO products.layout_category_groups (layout_id, category_group_id, meta, rank, image_id)
VALUES
('layout-1', 'group-1', '{ "meta-5": "meta-5" }', 1, 'image-group-1'),
('layout-2', 'group-2', '{ "meta-6": "meta-6" }', 1, 'image-group-2')
;

INSERT INTO products.category_groups (id, alias, title_tanker_key, meta, status)
VALUES
('group-1', 'al-group-1', 'title_tanker_key-4', '{ "meta-4": "meta-4" }', 'active'),
('group-2', 'al-group-2', 'title_tanker_key-5', '{ "meta-5": "meta-5" }', 'active'),
('group-unattached', 'al-group-unattached', 'title_tanker_key-6', '{ "meta-7": "meta-7" }', 'active')
;

INSERT INTO products.category_groups_images (category_group_id, image_id, image_dimensions)
VALUES
('group-2', 'image-group-2', (2, 2))
;
