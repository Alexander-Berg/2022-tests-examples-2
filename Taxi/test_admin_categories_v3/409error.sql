INSERT INTO products.virtual_categories (id, alias, title_tanker_key, meta, status)
VALUES
('category-11-1', 'layout-alias-5', 'title_tanker_key-1', '{ "meta-1": "meta-1" }', 'active'),
('category-11-2', 'layout-alias-6', 'title_tanker_key-2', '{ "meta-2": "meta-2" }', 'active'),
('category-11-3', 'layout-alias-7', 'title_tanker_key-3', '{ "meta-3": "meta-3" }', 'active'),
('category-unattached', 'al-category-unattached', 'title_tanker_key-3', '{ "meta-3": "meta-3" }', 'active')
;

INSERT INTO products.layouts (id, alias, meta, status)
VALUES
('layout-1', 'layout-alias-5', '{ "meta-1": "meta-1" }', 'active'),
('layout-2', 'layout-alias-6', '{ "meta-2": "meta-2" }', 'active')
;

INSERT INTO products.layout_category_groups (layout_id, category_group_id, meta, rank, image_id)
VALUES
('layout-1', 'group-1', '{ "meta-1": "meta-1" }', 1, 'image-group-1'),
('layout-2', 'group-2', '{ "meta-2": "meta-2" }', 1, 'image-group-2')
;

INSERT INTO products.layout_virtual_categories (layout_id, category_group_id, virtual_category_id, meta, rank)
VALUES
('layout-1', 'group-1', 'category-11-1', '{ "meta-11-1": "meta-1" }', 1),
('layout-2', 'group-2', 'category-11-2', '{ "meta-11-2": "meta-11-2" }', 1),
('layout-1', 'group-1', 'category-11-3', '{ "meta-11-3": "meta-3" }', 1)
;

INSERT INTO products.layout_virtual_categories_images (layout_id, category_group_id, virtual_category_id, image_id, dimensions)
VALUES
('layout-1', 'group-1', 'category-11-1', 'image-category-11-1', (2, 2)),
('layout-2', 'group-2', 'category-11-2', 'image-category-11-2', (2, 2)),
('layout-1', 'group-1', 'category-11-3', 'image-category-11-3', (2, 2)),
('layout-1', 'group-1', 'category-11-3', 'image-category-11-3', (4, 2))
;

INSERT INTO products.virtual_categories_images (virtual_category_id, image_id, image_dimensions)
VALUES
('category-11-2', 'image-category-11-2', (2, 2)),
('category-11-3', 'image-category-11-3', (2, 2)),
('category-11-3', 'image-category-11-3', (4, 2))
;
