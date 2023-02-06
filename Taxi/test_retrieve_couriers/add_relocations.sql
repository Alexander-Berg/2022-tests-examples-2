insert into
    uniform_courier_relocations (place_id, courier_id, reason, creator_id)
values
    (1, 3, 'first_give_out', 1),
    (1, 3, 'change_give_out', 1)
;

insert into
    uniform_courier_relocation_courier_uniform (uniform_courier_relocation_id, diff, courier_uniform_id, depremization, number)
values
    (2, 1, 4, null, 'TEST_NUMBER_4'),
    (2, 1, 4, 10, 'TEST_NUMBER_3')
;
