INSERT INTO products.layouts (id, alias, meta, status, created, title_tanker_key)
VALUES
('layout-1', 'layout-alias-1', '{ "meta-1": "meta-1" }', 'active', '2020-08-24 10:00:00+03', NULL),
('layout-2', 'layout-alias-2', '{ "meta-2": "meta-2" }', 'active', '2020-08-24 10:10:00+03', 'layout-tanker-key'),
('layout-3', 'layout-alias-3', '{ "meta-3": "meta-3" }', 'active', '2020-08-24 10:20:00+03', NULL),
('layout-disabled', 'layout-alias-disabled', '{ "meta-disabled": "meta-disabled" }', 'disabled', '2020-08-24 10:30:00+03', NULL)
;

INSERT INTO products.layout_category_groups (layout_id, category_group_id, meta, rank, image_id)
VALUES
('layout-1', 'group-1', '{ "meta-1": "meta-1" }', 1, 'image-group-1'),
('layout-1', 'group-12', '{ "meta-12": "meta-12" }', 2, 'image-group-12'),
('layout-1', 'group-13', '{ "meta-13": "meta-13" }', 4, 'image-group-13'),
('layout-2', 'group-2', '{ "meta-2": "meta-2" }', 1, 'image-group-2'),
('layout-2', 'group-23', '{ "meta-23": "meta-23" }', 1, 'image-group-23'),
('layout-2', 'group-12', '{ "meta-12": "meta-12" }', 3, 'image-group-12'),
('layout-3', 'group-3', '{ "meta-3": "meta-3" }', 2, 'image-group-3'),
('layout-3', 'group-13', '{ "meta-13": "meta-13" }', 1, 'image-group-13'),
('layout-3', 'group-23', '{ "meta-23": "meta-23" }', 3, 'image-group-23')
;

INSERT INTO products.layout_virtual_categories (layout_id, category_group_id, virtual_category_id, meta, rank)
VALUES
('layout-1', 'group-1', 'category-11-1', '{ "meta-11-1": "meta-11-1" }', 1),
('layout-1', 'group-1', 'category-11-2', '{ "meta-11-2": "meta-11-2" }', 2),
('layout-1', 'group-12', 'category-112-1', '{ "meta-112-1": "meta-112-1" }', 1),
('layout-1', 'group-12', 'category-112-2', '{ "meta-112-2": "meta-112-2" }', 1),
('layout-1', 'group-13', 'category-113-1', '{ "meta-113-1": "meta-113-1" }', 1),
('layout-2', 'group-2', 'category-22-1', '{ "meta-22-1": "meta-22-1" }', 1),
('layout-2', 'group-2', 'category-22-2', '{ "meta-22-2": "meta-22-2" }', 3),
('layout-2', 'group-2', 'category-22-3', '{ "meta-22-3": "meta-22-3" }', 4),
('layout-2', 'group-23', 'category-223-1', '{ "meta-223-1": "meta-223-1" }', 2),
('layout-2', 'group-12', 'category-212-1', '{ "meta-212-1": "meta-212-1" }', 1),
('layout-2', 'group-12', 'category-212-2', '{ "meta-212-2": "meta-212-2" }', 1),
('layout-3', 'group-3', 'category-33-1', '{ "meta-33-1": "meta-33-1" }', 1),
('layout-3', 'group-13', 'category-313-1', '{ "meta-313-1": "meta-313-1" }', 4),
('layout-3', 'group-23', 'category-323-1', '{ "meta-323-1": "meta-323-1" }', 1)
;

INSERT INTO products.layout_virtual_categories_images (layout_id, category_group_id, virtual_category_id, dimensions, image_id)
VALUES
('layout-1', 'group-1', 'category-11-1', (2, 2), 'image-category-11-1'),
('layout-1', 'group-1', 'category-11-2', (2, 4), 'image-category-11-2'),
('layout-1', 'group-12', 'category-112-1', (4, 2), 'image-category-112-1'),
('layout-1', 'group-12', 'category-112-2', (4, 4), 'image-category-112-2'),
('layout-1', 'group-13', 'category-113-1', (2, 2), 'image-category-113-1'),
('layout-2', 'group-2', 'category-22-1', (2, 2), 'image-category-22-1'),
('layout-2', 'group-2', 'category-22-2', (2, 2), 'image-category-22-2'),
('layout-2', 'group-2', 'category-22-3', (2, 4), 'image-category-22-3'),
('layout-2', 'group-23', 'category-223-1', (2, 2), 'image-category-223-1'),
('layout-2', 'group-12', 'category-212-1', (4, 4), 'image-category-212-1'),
('layout-2', 'group-12', 'category-212-2', (6, 2), 'image-category-212-2'),
('layout-3', 'group-3', 'category-33-1', (2, 2), 'image-category-33-1'),
('layout-3', 'group-13', 'category-313-1', (2, 2), 'image-category-313-1'),
('layout-3', 'group-23', 'category-323-1', (2, 2), 'image-category-323-1')
;
