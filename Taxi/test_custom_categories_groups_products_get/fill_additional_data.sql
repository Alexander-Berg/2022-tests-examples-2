insert into eats_nomenclature.custom_categories (id, name, external_id)
values (1, 'Кастомная категория 1', 1), (2, 'Пустая категория', 2);

insert into eats_nomenclature.assortments (id)
values (1), (2);

insert into eats_nomenclature.categories
    (id, name, origin_id, assortment_id, is_custom, custom_category_id)
values
    (1, 'Кастомная категория (1)', '6186038f-0d8c-4fa6-b22e-2a7ce50a374d', 1, true, 1),
    (2, 'Кастомная категория (1)', '8f307f42-f84a-4dd0-8395-857184c9f9f7', 2, true, 2);

insert into eats_nomenclature.categories_products
    (assortment_id, category_id, product_id, sort_order)
values
    (1, 1, 1, 100),
    (1, 1, 2, 100),
    (1, 1, 3, 100),
    (1, 1, 4, 100);

insert into eats_nomenclature.custom_categories_product_types (custom_category_id, product_type_id)
values (1, 1), (1, 2);
