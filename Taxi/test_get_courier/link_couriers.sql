insert into
    courier_uniforms (type_id, courier_id, used, number, count, size_id)
values
    (1, 1, False, null, 10, 1),
    (1, 2, False, null, 0, 1)
;

insert into
    uniform_courier_relocations (place_id, courier_id, reason, creator_id)
values
    (1, 1, 'first_give_out', 1),
    (1, 1, 'change_give_out', 1)
;

insert into
    uniform_courier_relocation_courier_uniform (uniform_courier_relocation_id, diff, courier_uniform_id, depremization)
values
    (1, 1, 1, null)
;
insert into
    general_couriers (id, vehicle_type)
values
    (1, 'vehicle'),
    (2, 'vehicle')
;
