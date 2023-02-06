INSERT INTO products.virtual_categories (id, alias, title_tanker_key, meta, status, created)
VALUES 
('virtual-category-1', 'alias-1', 'title_tanker_key-1', '{ "meta-1": "meta-1" }', 'active', '2020-08-24 10:10:00+03'),
('virtual-category-z', 'alias-z', 'title_tanker_key-z', '{ "meta-z": "meta-z" }', 'active', '2020-08-24 10:20:00+03')
;

INSERT INTO products.virtual_categories (id, alias, title_tanker_key, short_title_tanker_key, meta, status, created, deep_link)
VALUES
('virtual-category-3', 'alias-3', 'title_tanker_key-3', 'short_title_tanker_key-3', '{ "meta-3": "meta-3" }', 'active', '2020-08-24 11:00:00+03', 'category-deep-link')
;

INSERT INTO products.virtual_categories (id, alias, title_tanker_key, short_title_tanker_key, meta, status, created, special_category)
VALUES
('virtual-category-4', 'alias-4', 'title_tanker_key-4', 'short_title_tanker_key-4', '{ "meta-4": "meta-4" }', 'active', '2020-08-24 11:00:00+03', 'promo-caas')
;

INSERT INTO products.virtual_categories_subcategories (virtual_category_id, subcategory_id, rank)
VALUES 
('virtual-category-1', 'subcategory-1-1', 1),
('virtual-category-1', 'subcategory-1-3', 3),
('virtual-category-1', 'subcategory-1-2', 2),
('virtual-category-z', 'subcategory-z', 1),
('virtual-category-z', 'subcategory-b', 3),
('virtual-category-z', 'subcategory-a', 2),
('virtual-category-3', 'subcategory-31', 1),
('virtual-category-3', 'subcategory-32', 2)
;
