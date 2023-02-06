insert into
    courier_uniforms (type_id, courier_id, used, number, count, size_id)
values
    (1, 1, False, null, 10, 1),
    (1, 1, False, null, 10, 2),
    (1, 3, False, null, 10, 1),
    (1, 3, False, null, 10, 2)
;

insert into
    uniform_courier_relocations (place_id, courier_id, reason, creator_id)
values
    (1, 3, 'first_give_out', 1),
    (1, 3, 'change_give_out', 1)
;

insert into
    uniform_courier_relocation_courier_uniform (uniform_courier_relocation_id, diff, courier_uniform_id, courier_depremization_id)
values
    (2, 1, 3, null),
    (2, 1, 3, 10)
;

insert into
    general_couriers (id, vehicle_type)
values
    (3, 'courier-vehicle')
;
