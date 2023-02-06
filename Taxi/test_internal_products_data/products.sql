INSERT INTO catalog_wms.categories(category_id, status, name, description, rank, parent_id, images, legal_restrictions)
VALUES
('d9ef3613-c0ed-40d2-9fdc-3eed67f55aae', 'active', 'Корень 1', 'Корневая категория', 0, null, array[]::text[], array[]::text[]),
('61d24b27-0e8e-4173-a861-95c87802972f', 'active', 'Категория с товарами', 'Категория с товарами', 97, 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae', '{}', '{}')
;

INSERT INTO catalog_wms.goods(product_id, status, external_id, title, long_title, description, rank, amount_unit,
	amount_unit_alias, manufacturer, amount, images, legal_restrictions, pfc, ingredients, shelf_conditions, country, brand,
	measurements, important_ingredients, main_allergens, photo_stickers, custom_tags, logistic_tags, mark_count_pack, recycling_codes)
VALUES
('89cc6837-cb1e-11e9-b7ff-ac1f6b8569b3', 'active', 2903, 'Арбуз', 'Арбуз, 5 кг', 'Арбуз, 5 кг (описание)',
 97, 'кг', 'kilogram', NULL, 5.0000, '{"watermelon_template.jpg"}', '{}', 
 '{"(calories,100.000000)","(carbohydrate,10.000000)","(fat,15.6780000)","(protein,18.900000)"}', '{}', 
 '{"(store_conditions,Хранить нежно)","(after_open,14)","(shelf_life,12)"}', 'Россия', 'ООО Арбузы', NULL,
 '{"shugar"}', '{"fish"}', '{"photo.jpg"}', '{"halal"}', '{"hot"}', 2, '{"some_code"}'),
('88b4b661-aa33-11e9-b7ff-ac1f6b8569b3', 'active', 2657, 'Дыня', 'Дыня, 3,5 кг', 'Дыня, 3,5 кг (описание)', 
 88, 'кг', NULL, NULL, 3.5000, '{"melon_template.jpg"}', ARRAY['RU_18+'], '{}', '{}', '{}', 'Казахстан', NULL, '(1,2,3,4,5)',
 '{}', '{}', '{}', '{}', '{}', 1, '{}'),
('d36ff36d-cb3c-11e9-b7ff-ac1f6b8569b3', 'disabled', 2883, 'Батат', 'Батат, 500 г', 'Батат, 500 г (описание)',
 58, 'г', 'gram', NULL, 500.0000, '{"yam_template.jpg"}', '{}', 
 '{"(calories,114.000000)","(carbohydrate,16.000000)","(fat,17.500000)","(protein,18.900000)"}', '{}', 
 array[('store_conditions',''), ('after_open','0'), ('shelf_life','0')]::catalog_wms.key_value_pair[], NULL, 'ООО ААА',
 '(10,,,11,)', '{}', '{}', '{}', '{}', '{}', 1, '{}')
;

INSERT INTO catalog_wms.goods_categories (product_id, category_id)
VALUES
('89cc6837-cb1e-11e9-b7ff-ac1f6b8569b3', '61d24b27-0e8e-4173-a861-95c87802972f'),
('88b4b661-aa33-11e9-b7ff-ac1f6b8569b3', '61d24b27-0e8e-4173-a861-95c87802972f'),
('d36ff36d-cb3c-11e9-b7ff-ac1f6b8569b3', '61d24b27-0e8e-4173-a861-95c87802972f')
;
