INSERT INTO products.virtual_categories (id, alias, title_tanker_key, meta, status)
VALUES
('category-11-1', 'category-11-1-alias', 'category-11-1-title-tanker-key', '{ "category-11-1-meta": "category-11-1-meta" }', 'active'),
('category-11-2', 'category-11-2-alias', 'category-11-2-title-tanker-key', '{ "category-11-2-meta": "category-11-2-meta" }', 'active'),
('category-112-1', 'category-112-1-alias', 'category-112-1-title-tanker-key', '{ "category-112-1-meta": "category-112-1-meta" }', 'active'),
('category-112-2', 'category-112-2-alias', 'category-112-2-title-tanker-key', '{ "category-112-2-meta": "category-112-2-meta" }', 'active'),
('category-113-1', 'category-113-1-alias', 'category-113-1-title-tanker-key', '{ "category-113-1-meta": "category-113-1-meta" }', 'active'),
('category-212-1', 'category-212-1-alias', 'category-212-1-title-tanker-key', '{ "category-212-1-meta": "category-212-1-meta" }', 'active'),
('category-212-2', 'category-212-2-alias', 'category-212-2-title-tanker-key', '{ "category-212-2-meta": "category-212-2-meta" }', 'active'),
('category-22-1', 'category-22-1-alias', 'category-22-1-title-tanker-key', '{ "category-22-1-meta": "category-22-1-meta" }', 'active'),
('category-22-2', 'category-22-2-alias', 'category-22-2-title-tanker-key', '{ "category-22-2-meta": "category-22-2-meta" }', 'active'),
('category-22-3', 'category-22-3-alias', 'category-22-3-title-tanker-key', '{ "category-22-3-meta": "category-22-3-meta" }', 'active'),
('category-223-1', 'category-223-1-alias', 'category-223-1-title-tanker-key', '{ "category-223-1-meta": "category-223-1-meta" }', 'active'),
('category-313-1', 'category-313-1-alias', 'category-313-1-title-tanker-key', '{ "category-313-1-meta": "category-313-1-meta" }', 'active'),
('category-323-1', 'category-323-1-alias', 'category-323-1-title-tanker-key', '{ "category-323-1-meta": "category-323-1-meta" }', 'active'),
('category-33-1', 'category-33-1-alias', 'category-33-1-title-tanker-key', '{ "category-33-1-meta": "category-33-1-meta" }', 'active')
;

INSERT INTO products.virtual_categories_subcategories (virtual_category_id, subcategory_id, rank)
VALUES
('category-11-1', 'category-11-1-subcategory-1', 1),
('category-11-1', 'category-11-1-subcategory-2', 2),
('category-11-1', 'category-11-1-subcategory-3', 3),
('category-11-2', 'category-11-2-subcategory-a', 2),
('category-11-2', 'category-11-2-subcategory-z', 1),
('category-112-1', 'category-112-1-subcategory-1', 1),
('category-112-2', 'category-112-2-subcategory-1', 1),
('category-113-1', 'category-113-1-subcategory-1', 1),
('category-212-1', 'category-212-1-subcategory-1', 1),
('category-212-2', 'category-212-2-subcategory-1', 1),
('category-22-1', 'category-22-1-subcategory-1', 1),
('category-22-2', 'category-22-2-subcategory-1', 1),
('category-22-3', 'category-22-3-subcategory-1', 1),
('category-223-1', 'category-223-1-subcategory-1', 1),
('category-313-1', 'category-313-1-subcategory-1', 1),
('category-323-1', 'category-323-1-subcategory-1', 1),
('category-33-1', 'category-33-1-subcategory-1', 1),
('category-short-key', 'category-short-key-subcategory', 1)
;

INSERT INTO products.virtual_categories_images (virtual_category_id, image_id, image_dimensions)
VALUES
('category-11-1', 'category-11-1-image-1', (5, 5)),
('category-11-1', 'category-11-1-image-1', (2, 2)),
('category-11-1', 'category-11-1-image-2', (7, 7)),
('category-11-2', 'category-11-2-image-1', (5, 5)),
('category-112-1', 'category-112-1-image-1', (9, 9)),
('category-112-2', 'category-112-2-image-1', (2, 2)),
('category-113-1', 'category-113-1-image-1', (2, 2)),
('category-212-1', 'category-212-1-image-1', (2, 2)),
('category-212-2', 'category-212-2-image-1', (2, 2)),
('category-22-1', 'category-22-1-image-1', (2, 2)),
('category-22-2', 'category-22-2-image-1', (2, 2)),
('category-22-3', 'category-22-3-image-1', (2, 2)),
('category-223-1', 'category-223-1-image-1', (2, 2)),
('category-313-1', 'category-313-1-image-1', (2, 2)),
('category-323-1', 'category-323-1-image-1', (2, 2)),
('category-33-1', 'category-33-1-image-1', (2, 2))
;
