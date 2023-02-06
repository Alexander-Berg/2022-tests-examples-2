insert into eats_nomenclature.brands (id) values (1);
insert into eats_nomenclature.places (id, slug, stock_reset_limit) values (1, 'slug', 5);
insert into eats_nomenclature.brand_places (brand_id, place_id) values (1, 1);
insert into eats_nomenclature.assortments default values; 
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id)
values (1, 1, null);

insert into eats_nomenclature.categories_dictionary(id, name)
values (11, '1');

insert into eats_nomenclature.categories (id, public_id, assortment_id, name, origin_id, is_custom, is_base, is_restaurant)
values (1, 11, 1, '1', '1_origin', false, false, false);

insert into eats_nomenclature.places_categories (assortment_id, place_id, category_id, active_items_count)
values (1, 1, 1, 1);

insert into eats_nomenclature.categories_relations (category_id, parent_category_id, assortment_id, sort_order)
values (1, null, 1, 3);
