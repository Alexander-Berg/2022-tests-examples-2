insert into eats_nomenclature_viewer.brands(id, slug, name, is_enabled)
values
    (1, 'slug', 'name', true)
;

insert into eats_nomenclature_viewer.places(id, slug, is_enabled, brand_id)
values
    (1, 'slug', true, 1)
;

insert into eats_nomenclature_viewer.products(
    nmn_id, origin_id, brand_id, name, measure_unit, measure_value
)
values
    ('00000000-0000-0000-0000-000000000001', 'origin_id_1', 1, 'name', 'г', '1.0')
;
