INSERT INTO products.category_groups (id, alias, title_tanker_key, meta, status, created, short_title_tanker_key)
VALUES 
('category-group-1', 'group-alias-1', 'title_tanker_key-1', '{ "meta-1": "meta-1" }', 'active', '2020-08-24 10:00:00+03', NULL),
('category-group-2', 'group-alias-2', 'title_tanker_key-2', '{ "meta-2": "meta-2" }', 'active', '2020-08-24 10:10:00+03', NULL),
('category-group-3', 'group-alias-3', 'title_tanker_key-3', '{ "meta-3": "meta-3" }', 'active', '2020-08-24 10:20:00+03', NULL),
('category-group-disabled', 'group-alias-disabled', 'title_tanker_key-disabled', '{ "meta-disabled": "meta-disabled" }', 'disabled', '2020-08-24 10:30:00+03', NULL),
('category-group-no-images', 'group-alias-no-images', 'title_tanker_key-no-images', '{ "meta-no-images": "meta-no-images" }', 'active', '2020-08-24 10:40:00+03', NULL),
('category-group-short-tanker', 'group-alias-4', 'title_tanker_key-4', '{ "meta-4": "meta-4" }', 'active', '2020-08-24 10:30:00+03', 'short_title_tanker_key-4')
;

INSERT INTO products.category_groups_images (category_group_id, image_id, image_dimensions)
VALUES
('category-group-1', 'image-group-11', (2, 2)),
('category-group-1', 'image-group-12', (2, 6)),
('category-group-1', 'image-group-13', (2, 4)),
('category-group-2', 'image-group-21', (4, 2)),
('category-group-2', 'image-group-22', (4, 6)),
('category-group-2', 'image-group-23', (4, 4)),
('category-group-3', 'image-group-31', (6, 2)),
('category-group-3', 'image-group-32', (6, 6)),
('category-group-3', 'image-group-33', (6, 4)),
('category-group-disabled', 'image-group-disabled-1', (1, 3)),
('category-group-disabled', 'image-group-disabled-2', (1, 4))
;
