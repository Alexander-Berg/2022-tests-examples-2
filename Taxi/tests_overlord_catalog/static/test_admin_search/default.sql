BEGIN TRANSACTION;

INSERT INTO catalog_wms.categories(category_id, external_id, status, name, description, rank, parent_id, images, legal_restrictions)
VALUES
('d9ef3613-c0ed-40d2-9fdc-000000000001', 'root_category', 'active', 'Корень 2', 'Корневая категория', 0, null, array[]::text[], array[]::text[]),
('61d24b27-0e8e-4173-a861-000000000002', 'child_category_1', 'active', 'Дочерняя категория 1', 'Дочерняя категория 1', 97, 'd9ef3613-c0ed-40d2-9fdc-000000000001', '{}', '{}'),
('884d1dec-b1d8-4638-bbc3-000000000003', 'child_category_2', 'active', 'Дочерняя категория 2', 'Дочерняя категория 2', 329, '61d24b27-0e8e-4173-a861-000000000002', '{}', '{}')
;

INSERT INTO catalog_wms.goods(product_id, status, external_id, title, long_title, description, rank, amount_unit, amount, images, legal_restrictions, pfc, ingredients)
VALUES
('89cc6837-cb1e-11e9-b7ff-000000000001', 'active', 1234, 'Товар 1', 'Товар 111111', 'Товар 111111', 97, 'кг', 5.0000, '{}', '{}', '{}', '{}'),
('88b4b661-aa33-11e9-b7ff-000000000002', 'disabled', 5678, 'Товар 2', 'Товар 222222', 'Товар 222222', 88, 'кг', 3.5000, '{}', '{}', '{}', '{}'),
('d36ff36d-cb3c-11e9-b7ff-000000000003', 'active', 9101, 'Товар 3', 'Товар 333333', 'Товар 333333', 58, 'г', 500.0000, '{}', '{}', '{}', '{}')
;

INSERT INTO catalog_wms.goods_categories (product_id, category_id)
VALUES
('89cc6837-cb1e-11e9-b7ff-000000000001', '61d24b27-0e8e-4173-a861-000000000002'),
('88b4b661-aa33-11e9-b7ff-000000000002', '884d1dec-b1d8-4638-bbc3-000000000003'),
('d36ff36d-cb3c-11e9-b7ff-000000000003', '61d24b27-0e8e-4173-a861-000000000002'),
('d36ff36d-cb3c-11e9-b7ff-000000000003', '884d1dec-b1d8-4638-bbc3-000000000003')
;

COMMIT TRANSACTION;
