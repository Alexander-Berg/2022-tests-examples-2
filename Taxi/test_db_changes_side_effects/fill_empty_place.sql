insert into eats_nomenclature.brands (id, slug) values (777, 'lavka'),(888, 'old_brand');
insert into eats_nomenclature.places (id, slug, is_enabled) values (1, '1', true);
insert into eats_nomenclature.brand_places (brand_id, place_id) values (777, 1);
insert into eats_nomenclature.market_brand_places (brand_id, place_id, business_id, partner_id, feed_id) values (777, 1, 10, 20, 30);
insert into eats_nomenclature.assortments default values;
insert into eats_nomenclature.assortments default values;
insert into eats_nomenclature.place_assortments (place_id, assortment_id, in_progress_assortment_id)
values (1, 1, 2);

insert into eats_nomenclature.vendors (name, country)
values ('vendor_1', 'country_1');

insert into eats_nomenclature.categories (assortment_id, name, origin_id)
values (1, 'category_1', 'category_1_origin'),
       (2, 'category_1', 'category_1_origin');

insert into eats_nomenclature.categories_relations (assortment_id, category_id,  sort_order)
values (1, 1, 100);

insert into eats_nomenclature.places_categories(assortment_id, place_id, category_id, active_items_count)
values (1, 1, 1, 0),
       (2, 1, 2, 0);

