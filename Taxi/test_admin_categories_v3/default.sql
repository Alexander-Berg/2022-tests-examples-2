INSERT INTO products.virtual_categories (id, alias, title_tanker_key, meta, status, created)
VALUES 
('virtual-category-1', 'alias-1', 'title_tanker_key-1', '{ "meta-1": "meta-1" }', 'active', '2020-08-24 10:10:00+03'),
('virtual-category-2', 'alias-2', 'title_tanker_key-2', '{ "meta-2": "meta-2" }', 'active', '2020-08-24 10:20:00+03'),
('virtual-category-3', 'alias-3', 'title_tanker_key-3', '{ "meta-3": "meta-3" }', 'active', '2020-08-24 10:30:00+03'),
('virtual-category-no-subs', 'alias-no-subs', 'title_tanker_key-no-subs', '{ "meta-no-subs": "meta-no-subs" }', 'active', '2020-08-24 10:00:00+03'),
('virtual-category-disabled', 'alias-disabled', 'title_tanker_key-disabled', '{ "meta-disabled": "meta-disabled" }', 'disabled', '2020-08-24 10:40:00+03'),
('virtual-category-no-images', 'alias-no-images', 'title_tanker_key-no-images', '{ "meta-no-images": "meta-no-images" }', 'active', '2020-08-24 10:50:00+03'),
('virtual-category-multi-dimensions', 'alias-multi-dimensions', 'title_tanker_key-multi-dimensions', '{ "meta-multi-dimensions": "meta-multi-dimensions" }', 'active', '2020-08-24 10:10:00+03')
;

INSERT INTO products.virtual_categories (id, alias, title_tanker_key, short_title_tanker_key, meta, status, created)
VALUES
('virtual-category-short-tanker', 'alias-4', 'title_tanker_key-4', 'short_title_tanker_key-4', '{ "meta-4": "meta-4" }', 'active', '2020-08-24 11:00:00+03')
;

INSERT INTO products.virtual_categories (id, alias, title_tanker_key, meta, status, created, is_special_category)
VALUES
('virtual-category-special', 'alias-special', 'title_tanker_key-1', '{meta-1}', 'active', '2020-08-24 10:10:00+03', TRUE)
;

INSERT INTO products.virtual_categories (id, alias, title_tanker_key, meta, status, created, deep_link)
VALUES
('virtual-category-with-deeplink', 'alias-deeplink', 'title_tanker_key-1', '{meta-1}', 'active', '2020-08-24 10:10:00+03', 'category-deep-link')
;

INSERT INTO products.virtual_categories (id, alias, title_tanker_key, meta, status, created, special_category)
VALUES
('virtual-category-with-special-category', 'alias-special-category', 'title_tanker_key-1', '{meta-1}', 'active', '2020-08-24 10:10:00+03', 'promo-caas')
;

INSERT INTO products.virtual_categories_subcategories (virtual_category_id, subcategory_id, rank)
VALUES 
('virtual-category-1', 'subcategory-for-1', 1),
('virtual-category-2', 'subcategory-for-2', 1),
('virtual-category-3', 'subcategory-for-3', 1),
('virtual-category-1', 'subcategory-for-12', 2),
('virtual-category-2', 'subcategory-for-12', 2),
('virtual-category-1', 'subcategory-for-123', 3),
('virtual-category-2', 'subcategory-for-123', 3),
('virtual-category-3', 'subcategory-for-123', 2),
('virtual-category-disabled', 'subcategory-for-disabled', 1),
('virtual-category-no-images', 'subcategory-for-no-images', 1)
;

INSERT INTO products.virtual_categories_images (virtual_category_id, image_id, image_dimensions)
VALUES
('virtual-category-1', 'image11', (2, 2)),
('virtual-category-1', 'image12', (2, 6)),
('virtual-category-1', 'image13', (2, 4)),
('virtual-category-2', 'image21', (4, 2)),
('virtual-category-2', 'image22', (4, 6)),
('virtual-category-2', 'image23', (4, 4)),
('virtual-category-3', 'image31', (6, 2)),
('virtual-category-3', 'image32', (6, 6)),
('virtual-category-3', 'image33', (6, 4)),
('virtual-category-no-subs', 'image-for-no-subs-1', (3, 2)),
('virtual-category-no-subs', 'image-for-no-subs-2', (3, 4)),
('virtual-category-disabled', 'image-for-disabled-1', (1, 3)),
('virtual-category-disabled', 'image-for-disabled-2', (1, 4)),
('virtual-category-multi-dimensions', 'image-for-md-1', (2, 2)),
('virtual-category-multi-dimensions', 'image-for-md-1', (4, 2)),
('virtual-category-multi-dimensions', 'image-for-md-2', (6, 2))
;
