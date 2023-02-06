INSERT INTO products.category_groups (id, alias, title_tanker_key, meta, status)
VALUES
('group-1', 'group-1-alias', 'group-1-title-tanker-key', '{ "group-1-meta": "group-1-meta" }', 'disabled')
;

INSERT INTO products.category_groups_images (category_group_id, image_id)
VALUES
('group-1', 'group-1-image-1')
;


INSERT INTO products.virtual_categories (id, alias, title_tanker_key, meta, status)
VALUES
('category-11-1', 'category-11-1-alias', 'category-11-1-title-tanker-key', '{ "category-11-1-meta": "category-11-1-meta" }', 'disabled')
;

INSERT INTO products.virtual_categories_subcategories (virtual_category_id, subcategory_id)
VALUES
('category-11-1', 'category-11-1-subcategory-1')
;

INSERT INTO products.virtual_categories_images (virtual_category_id, image_id, image_dimensions)
VALUES
('category-11-1', 'category-11-1-image-1', (5, 5))
;
