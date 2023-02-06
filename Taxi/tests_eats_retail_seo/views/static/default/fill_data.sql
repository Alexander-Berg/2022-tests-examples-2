insert into eats_retail_seo.categories (id, name, image_url)
values
(1, 'category_name_1', 'image_url_1'),
(2, 'category_name_2', 'image_url_2'),
(3, 'category_name_3', 'image_url_3'),
(4, 'category_name_4', 'image_url_4'),
(5, 'category_name_5', 'image_url_5'),
(6, 'category_name_6', 'image_url_6');

insert into eats_retail_seo.categories_relations (category_id, parent_category_id)
values (5, null),
       (6, 5),
       (4, null),  
       (3, 4),
       (1, 4),
       (2, 3);

insert into eats_retail_seo.product_types (name)
values
('product_type_1'),
('product_type_2'),
('product_type_3'),
('product_type_4');

insert into eats_retail_seo.categories_product_types (category_id, product_type_id)
values
(1, 1),
(1, 2),
(2, 3),
(5, 4),
(6, 4);

insert into eats_retail_seo.product_brands (name)
values
('product_brand_1'),
('product_brand_2'),
('product_brand_3');

insert into eats_retail_seo.product_types_product_brands(product_type_id, product_brand_id)
values
(1, 1),
(2, 2),
(2, 3),
(3, 3);

insert into eats_retail_seo.seo_queries (product_type_id, product_brand_id, is_enabled)
values
(1, 1, true),
(2, 2, true),
(3, 3, true),
(3, null, true),
(null, 3, true),
(1, null, false),
(2, 3, true),
(4, null, true),
(4, 3, true);

insert into eats_retail_seo.generated_seo_queries_data (seo_query_id, slug, query, title, description, priority)
values
(1, 'old_slug_1', 'query_1', 'title_1', 'description_1', 100),
(2, 'old_slug_2', 'query_2', 'title_2', 'description_2', 90),
(3, 'slug_3', 'query_3', 'title_3', 'description_3', 80),
(4, 'slug_4', 'query_4', 'title_4', 'description_4', 85),
(5, 'slug_5', 'query_5', 'title_5', 'description_5', 95),
(6, 'slug_6_disabled', 'query_6', 'title_6', 'description_6', 101),
(7, 'slug_7', 'query_7', 'title_7', 'description_7', 75),
(8, 'slug_8', 'query_8', 'title_8', 'description_8', 20);

insert into eats_retail_seo.manual_seo_queries_data (seo_query_id, slug, query, title, description, priority)
values
(1, 'new_slug_1', 'new_query_1', 'new_title_1', 'new_description_1', 100),
(2, 'new_slug_2', 'new_query_2', 'new_title_2', 'new_description_2', 90);
