insert into
    courier_services (
    name,
    inn,
    region_ids,
    created_at,
    updated_at
)
select
    'test_service_' || a::text,
    '770000000' || a::text,
    to_jsonb('{1,2,3}'::int[]),
    '2017-09-08 00:00:00.00+00:00',
    '2017-09-08 00:00:00.00+00:00'
from
    generate_series(1, 5) a
;

insert into
    couriers (
    first_name,
    middle_name,
    last_name,
    phone_pd_id,
    eda_id,
    work_region_id,
    courier_project_type_id,
    courier_work_status_id,
    courier_service_id,
    created_at,
    updated_at
)
select
    'Курьер' || a::text,
    case
        when a % 2 = 0 then
            null
        else
            'Курьерович' || a::text
    end,
    'Курьеров' || a::text,
    case
        when a % 4 = 0 then
            '38d9c9ed14cf46538263a0a51f8a473a'
        when a % 4 = 1 then
            '48d9c9ed14cf46538263a0a51f8a473a'
        when a % 4 = 2 then
            '58d9c9ed14cf46538263a0a51f8a473a'
        when a % 4 = 3 then
            '68d9c9ed14cf46538263a0a51f8a473a'
    end,
    250000 + a,
    a % 2 + 1,
    case
        when a % 3 = 0 then
            1
        when a % 3 = 1 then
            2
        else
            null
    end,
    a % 2 + 1,
    a % 5 + 1,
    '2017-09-08 00:00:00.00+00:00',
    '2017-09-08 00:00:00.00+00:00'
from
    generate_series(1, 20) a
;


insert into
    courier_uniforms (type_id, courier_id, used, number, count, size_id)
values
    (1, 1, False, 'TEST_NUMBER', 10, 1),
    (2, 1, False, null, 1, 1),
    (1, 2, False, 'TEST_NUMBER_2', 3, 1),
    (2, 3, False, null, 1, 2)
;
