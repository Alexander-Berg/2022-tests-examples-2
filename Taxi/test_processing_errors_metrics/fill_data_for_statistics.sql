insert into eats_nomenclature.brands (id, slug)
values (1, 'brand1'),
       (2, 'brand2'),
       (3, 'brand3');
insert into eats_nomenclature.places (id, slug, is_enabled)
values (1, 'place1', true),
       (2, 'place2', false),
       (3, 'place3', true),
       (4, 'place4', true),
       (5, 'place5', true),
       (6, 'place6', true),
       (7, 'place7', true),
       (8, 'place8', true),
       (9, 'place9', true),
       (10, 'place10', true),
       (11, 'place11', true),
       (12, 'place12', true),
       (13, 'place13', true),
       (14, 'place14', true),
       (15, 'place15', true);

insert into eats_nomenclature.brand_places (brand_id, place_id)
values (1, 1),
       (1, 2),
       (2, 3),
       (2, 4),
       (2, 5),
       (2, 6),
       (2, 7),
       (2, 8),
       (2, 9),
       (2, 10),
       (2, 11),
       (3, 12),
       (2, 13),
       (2, 14),
       (2, 15);

insert into eats_nomenclature.assortment_traits (brand_id, assortment_name)
values (1, 'assortment_name_11'),
       (1, 'assortment_name_12'),
       (2, 'assortment_name_1'),
       (2, 'assortment_name_2');

insert into eats_nomenclature.place_default_assortments(place_id, trait_id)
values
       (2, 1),
       (4, 1),
       (15, 1);

insert into eats_nomenclature.places_processing_last_status_v2
(place_id, task_type, status, task_error, task_warnings, status_or_text_changed_at)
values (1, 'price', 'processed', null, null, now() - interval '1 hours'),
       (1, 'stock', 'processed', null, null, now() - interval '1 hours'),
       (1, 'availability', 'processed', null, null, now() - interval '1 hours'),
       (2, 'price', 'failed', 'DB error occurred while processing assortment', null, now() - interval '1 hours'),
       (2, 'stock', 'failed', 'Something failed while processing assortment', null, now() - interval '1 hours'),
       (2, 'availability', 'failed', 'DB error occurred while processing assortment', null, now() - interval '1 hours'),
       (3, 'price', 'processed', null, null, now() - interval '1 hours'),
       (4, 'stock', 'processed', null, null, now() - interval '1 hours'),
       (8, 'stock', 'processed', null, null, now() - interval '1 hours'),
       (13, 'price', 'failed', 'DB error occurred while processing assortment', null, now() - interval '1 hours'),
       (13, 'stock', 'failed', 'Something failed while processing assortment', null, now() - interval '1 hours'),
       (13, 'availability', 'failed', 'DB error occurred while processing assortment', null, now() - interval '3 minutes');

insert into eats_nomenclature.assortments(id, created_at)
values (1, now()),
       (2, now() - interval '10 hours'),
       (3, now() - interval '10 hours'),
       (4, now() - interval '10 hours');

insert into eats_nomenclature.place_assortments_processing_last_status
(place_id, assortment_id, trait_id, status, task_error, task_warnings, status_or_text_changed_at)
values (1, 1, null, 'processed', null, null, now() - interval '1 hours'),
       -- errors for custom trait
       (2, 1, 2, 'failed', 'New non-default assortment is potentially destructive', null, now() - interval '24 hours'),
        -- errors for default trait
       (2, 1, 1, 'failed', 'Something failed while processing assortment', null, now() - interval '1 hours'),
       (3, 1, null, 'failed', 'New partner assortment is potentially destructive', null, now() - interval '1 hours'),
       (4, 1, 1, 'failed', 'New assortment has too much unavailable products', null, now() - interval '1 hours'),
       (4, 1, null, 'failed', 'New assortment has too much products with zero stocks', null, now() - interval '1 hours'),
       (5, 1, null, 'failed', 'New assortment has too much products with zero stocks', null, now() - interval '1 hours'),
       (6, 1, null, 'failed', 'New assortment has too much products with zero prices', null, now() - interval '1 hours'),
       (7, 1, null, 'failed', 'New assortment has too much products without images', null, now() - interval '1 hours'),
       (14, 1, null, 'failed', 'DB error occurred while processing assortment', null, now() - interval '1 hours'),
       (15, 1, 1, 'failed', 'New default assortment is potentially destructive', null, now() - interval '1 hours');

insert into eats_nomenclature.place_assortments
(place_id, assortment_id, in_progress_assortment_id, trait_id, assortment_activated_at)
values (1, 1, 2, null, now() - interval '1 hours'),
       (2, null, 2, null, null),
       (3, 3, null, null, now() - interval '3 hours'),
       (3, 3, null, 1, now() - interval '1 hours'),
       (3, 3, null, 2, now() - interval '1 hours'),
       (4, 3, 4, null, now() - interval '1 hours'),
       (4, 3, 4, 1, now() - interval '3 hours'),
       (4, 3, 4, 2, now() - interval '1 hours'),
       (5, 3, 4, null, now() - interval '1 hours'),
       (6, 3, 4, null, now() - interval '1 hours'),
       (7, 3, 4, null, null),  -- assortment_activated_at is not filled yet
       (8, null, 4, null, null),
       (9, null, 4, null, null),
       (10, null, 4, null, null),
       (11, 3, 4, null, now() - interval '3 hours'),
       (12, 3, 4, null, now() - interval '3 hours');

insert into eats_nomenclature.place_update_statuses
(place_id, enabled_at, price_update_started_at, availability_update_started_at, stock_update_started_at)
values (1, now() - interval '3 hours', now() - interval '1 hours', now() - interval '1 hours', now() - interval '1 hours'),
       (2, now() - interval '3 hours', now() - interval '3 hours', now() - interval '3 hours', now() - interval '3 hours'),
       (3, now() - interval '3 hours', now() - interval '3 hours', now() - interval '3 hours', now() - interval '3 hours'),
       (4, now() - interval '3 hours', now() - interval '1 hours', now() - interval '1 hours', now() - interval '1 hours'),
       (5, now() - interval '3 hours', now() - interval '3 hours', now() - interval '1 hours', now() - interval '1 hours'),
       (6, now() - interval '3 hours', now() - interval '1 hours', now() - interval '3 hours', now() - interval '1 hours'),
       (7, now() - interval '3 hours', now() - interval '1 hours', now() - interval '1 hours', now() - interval '3 hours'),
       (8, now() - interval '3 hours', now() - interval '1 hours', now() - interval '1 hours', now() - interval '1 hours'),
       (9, now() - interval '3 hours', now() - interval '3 hours', now() - interval '3 hours', now() - interval '3 hours'),
       (10, now() - interval '30 minutes', now() - interval '3 hours', now() - interval '3 hours', now() - interval '3 hours'),
       (11, now() - interval '30 minutes', now() - interval '3 hours', now() - interval '3 hours', now() - interval '3 hours'),
       (12, now() - interval '3 hours', now() - interval '3 hours', now() - interval '3 hours', now() - interval '3 hours');
