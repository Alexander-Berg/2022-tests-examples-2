INSERT INTO products.layouts (id, alias, meta, status, created)
VALUES
('layout-1', 'layout-alias-1', '{ "meta-1": "meta-1" }', 'active', '2020-08-24 10:00:00+03'),
('layout-2', 'layout-alias-2', '{ "meta-2": "meta-2" }', 'active', '2020-08-24 10:10:00+03'),
('layout-3', 'layout-alias-3', '{ "meta-3": "meta-3" }', 'active', '2020-08-24 10:20:00+03')
;

INSERT INTO products.layout_category_groups (layout_id, category_group_id, meta, rank, image_id)
VALUES
('layout-1', 'group-1', '{ "meta-1": "meta-1" }', 1, 'image-group-1'),
('layout-1', 'group-2', '{ "meta-2": "meta-2" }', 3, 'image-group-2'),
('layout-1', 'group-3', '{ "meta-2": "meta-2" }', 2, 'image-group-3'),
('layout-2', 'group-a', '{ "meta-a": "meta-a" }', 2, 'image-group-a'),
('layout-2', 'group-b', '{ "meta-b": "meta-b" }', 3, 'image-group-b'),
('layout-2', 'group-z', '{ "meta-z": "meta-z" }', 1, 'image-group-z')
;

INSERT INTO products.layout_virtual_categories (layout_id, category_group_id, virtual_category_id, meta, rank)
VALUES
('layout-1', 'group-1', 'category-1-1', '{ "meta-1-1": "meta-1-1" }', 1),
('layout-1', 'group-1', 'category-1-2', '{ "meta-1-2": "meta-1-2" }', 2),
('layout-1', 'group-2', 'category-2-1', '{ "meta-2-1": "meta-2-1" }', 2),
('layout-1', 'group-2', 'category-2-2', '{ "meta-2-2": "meta-2-2" }', 1),
('layout-1', 'group-3', 'category-3-1', '{ "meta-3-1": "meta-3-1" }', 1),
('layout-2', 'group-a', 'category-a-1', '{ "meta-a-1": "meta-a-1" }', 1),
('layout-2', 'group-a', 'category-a-2', '{ "meta-a-2": "meta-a-2" }', 3),
('layout-2', 'group-a', 'category-a-3', '{ "meta-a-3": "meta-a-3" }', 2),
('layout-2', 'group-b', 'category-b-1', '{ "meta-b-1": "meta-b-1" }', 1),
('layout-2', 'group-z', 'category-z-1', '{ "meta-z-1": "meta-z-1" }', 2),
('layout-2', 'group-z', 'category-z-2', '{ "meta-z-2": "meta-z-2" }', 1)
;

INSERT INTO products.layout_virtual_categories_images (layout_id, category_group_id, virtual_category_id, dimensions, image_id)
VALUES
('layout-1', 'group-1', 'category-1-1', (2, 2), 'image-category-1-1'),
('layout-1', 'group-1', 'category-1-1', (4, 2), 'image-category-1-1'),
('layout-1', 'group-1', 'category-1-2', (3, 2), 'image-category-1-2'),
('layout-1', 'group-2', 'category-2-1', (4, 2), 'image-category-2-1'),
('layout-1', 'group-2', 'category-2-2', (4, 2), 'image-category-2-2'),
('layout-1', 'group-3', 'category-3-1', (2, 2), 'image-category-3-1'),
('layout-2', 'group-a', 'category-a-1', (2, 2), 'image-category-a-1'),
('layout-2', 'group-a', 'category-a-2', (3, 2), 'image-category-a-2'),
('layout-2', 'group-a', 'category-a-3', (2, 2), 'image-category-a-3'),
('layout-2', 'group-a', 'category-a-3', (4, 2), 'image-category-a-3'),
('layout-2', 'group-b', 'category-b-1', (2, 2), 'image-category-b-1'),
('layout-2', 'group-z', 'category-z-1', (4, 2), 'image-category-z-1'),
('layout-2', 'group-z', 'category-z-2', (6, 2), 'image-category-z-2')
;
