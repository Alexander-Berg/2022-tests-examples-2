insert into
    regions (name)
values
    ('Москва'),
    ('Ярославль')
;


insert into
    courier_project_types (name, description)
values
    ('eda', 'Еда'),
    ('lavka', 'Лавка')
;

insert into
    courier_work_statuses (name, description)
values
    ('active', 'Активен'),
    ('dismissed', 'Уволен'),
    ('deactivated', 'Деактивирован')
;


insert into
    countries (name)
values
    ('Российская Федерация'),
    ('Перу')
;

insert into
    courier_services (name, inn, region_ids)
values
    ('Autotest courier service', '1234567890', '[1, 3, 5]'::json)
;

insert into
    courier_types (name, description)
values
    ('pedestrian', 'Пешеход'),
    ('bicycle', 'Велосипед'),
    ('vehicle', 'Автомобиль'),
    ('motorcycle', 'Мотоцикл'),
    ('electric_bicycle', 'Электрический велосипед')
;

insert into
    courier_billing_types (name, description)
values
    ('self_employed', 'Самозанят'),
    ('courier_service', 'Курьерская служба')
;
