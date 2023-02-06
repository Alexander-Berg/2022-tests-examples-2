begin;

create table regions
(
    id serial primary key,
    name varchar(255) not null,
    created_at timestamp(0),
    updated_at timestamp(0)
);

create table courier_project_types
(
    id serial primary key,
    name varchar(255) not null,
    description varchar(255) not null,
    created_at timestamp(0),
    updated_at timestamp(0)
);

create table courier_work_statuses
(
    id serial primary key,
    name varchar(255) not null,
    description varchar(255) not null,
    created_at timestamp(0),
    updated_at timestamp(0)
);

create table courier_billing_types
(
    id serial not null
        constraint courier_billing_types_pkey
            primary key,
    name varchar(255) not null
        constraint courier_billing_types_name_unique
            unique,
    description varchar(255) not null,
    created_at timestamp(0),
    updated_at timestamp(0)
);

create table courier_services
(
    id serial not null
        constraint courier_services_pkey
            primary key,
    name varchar(255) not null,
    inn varchar(255) not null,
    region_ids jsonb not null,
    created_at timestamp(0),
    updated_at timestamp(0)
);

create table couriers
(
    id serial primary key,
    first_name varchar(255) not null,
    middle_name varchar(255),
    last_name varchar(255) not null,
    phone_pd_id varchar(255) not null,
    eda_id integer not null,
    work_region_id integer not null
        references regions (id) on delete restrict,
    courier_project_type_id integer
        references courier_project_types (id) on delete restrict,
    courier_work_status_id integer not null
        references courier_work_statuses (id) on delete restrict,
    created_at timestamp(0),
    updated_at timestamp(0),
    courier_billing_type_id integer null references courier_billing_types (id) on delete cascade on update cascade,
    courier_service_id integer null references courier_services (id) on delete cascade on update cascade,
    work_status_updated_at timestamp(0),
    comment varchar(255),
    is_deaf_mute smallint,
    is_picker smallint,
    is_dedicated_picker smallint,
    is_storekeeper smallint
);

create unique index couriers_eda_id_unique
    on couriers using btree (eda_id);
create index couriers_phone_pd_id
    on couriers using btree (phone_pd_id);
create index couriers_last_name_first_name_middle_name
    on couriers using btree (last_name, first_name, middle_name);

commit;


create type courier_v2 as
(
    id integer,
    first_name varchar(255),
    middle_name varchar(255),
    last_name varchar(255),
    phone_pd_id varchar(255),
    eda_id integer,
    work_region_id integer,
    courier_project_type_id integer,
    courier_work_status_id integer,
    created_at timestamp(0),
    updated_at timestamp(0),
    courier_billing_type_id integer,
    courier_service_id integer
);

create type courier_v3 as
(
    id integer,
    first_name varchar(255),
    middle_name varchar(255),
    last_name varchar(255),
    phone_pd_id varchar(255),
    eda_id integer,
    work_region_id integer,
    courier_project_type_id integer,
    courier_work_status_id integer,
    created_at timestamp(0),
    updated_at timestamp(0),
    courier_billing_type_id integer,
    courier_service_id integer,
    work_status_updated_at timestamp(0),
    comment varchar(255),
    is_deaf_mute smallint,
    is_picker smallint,
    is_dedicated_picker smallint,
    is_storekeeper smallint
);



create type courier_service_v1 as
(
    id integer,
    name varchar(255),
    inn varchar(255),
    region_ids json
);

create table uniform_types
(
    id bigserial not null
        constraint uniform_types_pkey
            primary key,
    name varchar(255) not null,
    description varchar(255),
    created_at timestamp(0),
    updated_at timestamp(0),
    has_number boolean default false not null,
    max_amount integer not null
);

create table uniform_sizes
(
    id bigserial not null
        constraint uniform_sizes_pkey
            primary key,
    name varchar(255) not null,
    created_at timestamp(0),
    updated_at timestamp(0)
);

create table courier_uniforms
(
    id bigserial not null
        constraint courier_uniforms_pkey
            primary key,
    type_id integer not null
        constraint courier_uniforms_type_id_foreign
            references uniform_types
            on update cascade on delete cascade,
    courier_id integer not null
        constraint courier_uniforms_courier_id_foreign
            references couriers
            on update cascade on delete cascade,
    used boolean not null,
    number varchar(255)
        constraint courier_uniforms_branding_number_unique
            unique,
    count integer not null,
    created_at timestamp(0),
    updated_at timestamp(0),
    size_id integer not null
        constraint courier_uniforms_size_id_foreign
            references uniform_sizes
            on update cascade on delete cascade,
    constraint courier_uniforms_type_id_courier_id_used_size_id_unique
        unique (type_id, courier_id, used, size_id)
);

create table vehicles
(
    id serial not null
        constraint vehicles_pkey
            primary key
);

create table vehicle_courier_assignment_histories
(
    id serial not null
        constraint vehicle_courier_assignment_histories_pkey
            primary key,
    courier_id integer not null
        constraint vehicle_courier_assignment_histories_courier_id_foreign
            references couriers
            on delete cascade,
    vehicle_id integer not null
        constraint vehicle_courier_assignment_histories_vehicle_id_foreign
            references vehicles
            on delete cascade,
    unassigned_at timestamp(0),
    assigned_at timestamp(0) default CURRENT_TIMESTAMP not null
);

create index vehicle_courier_assignment_histories_courier_id_index
    on vehicle_courier_assignment_histories (courier_id);

create index vehicle_courier_assignment_histories_vehicle_id_index
    on vehicle_courier_assignment_histories (vehicle_id);

create table places
(
    id serial not null
        constraint places_pkey
            primary key,
    name varchar(255) not null,
    full_address varchar(255) not null,
    created_at timestamp(0),
    updated_at timestamp(0),
    deleted_at timestamp(0),
    description varchar(255),
    location jsonb,
    region_id integer
        constraint places_region_id_foreign
            references regions
                on update cascade on delete cascade,
    status varchar(255) default 'active'::character varying not null,
    place_types jsonb default '[]'::jsonb not null,
    inventory_types jsonb default '[]'::jsonb not null
);

create table partners
(
    id serial not null
        constraint lessors_pkey
            primary key,
    name varchar(255) not null
        constraint lessors_name_unique
            unique,
    full_organization_name varchar(255),
    description varchar(255),
    email_pd_id varchar(60)
        constraint lessors_email_pd_id_unique
            unique,
    phone_pd_id varchar(60)
        constraint lessors_phone_pd_id_unique
            unique,
    tin_pd_id varchar(60)
        constraint lessors_tin_pd_id_unique
            unique,
    courier_service_id integer,
    created_at timestamp(0),
    updated_at timestamp(0),
    deleted_at timestamp(0),
    type varchar(255)
);

create table users
(
    id serial not null
        constraint users_pkey
            primary key,
    type varchar(255) not null,
    created_at timestamp(0),
    updated_at timestamp(0),
    deleted_at timestamp(0),
    name varchar(255),
    surname varchar(255),
    patronymic varchar(255),
    status varchar(255),
    profession varchar(255),
    company varchar(255),
    telegram_login_pd_id varchar(255),
    phone_pd_id varchar(255),
    partner_id integer
        constraint users_partner_id_foreign
            references partners
);

create table uniform_courier_relocations
(
    id bigserial not null
        constraint uniform_courier_relocations_pkey
            primary key,
    place_id integer not null
        constraint uniform_courier_relocations_place_id_foreign
            references places
                on update cascade on delete cascade,
    courier_id integer not null
        constraint uniform_courier_relocations_courier_id_foreign
            references couriers
                on update cascade on delete cascade,
    reason varchar(255) not null,
    creator_id integer not null
        constraint uniform_courier_relocations_creator_id_foreign
            references users
                on update cascade on delete cascade,
    created_at timestamp(0),
    updated_at timestamp(0),
    comment varchar(255)
);

create table place_uniforms
(
    id bigserial not null
        constraint place_uniforms_pkey
            primary key,
    type_id integer not null
        constraint place_uniforms_type_id_foreign
            references uniform_types
                on update cascade on delete cascade,
    place_id integer not null
        constraint place_uniforms_place_id_foreign
            references places
                on update cascade on delete cascade,
    used boolean not null,
    count integer not null,
    created_at timestamp(0),
    updated_at timestamp(0),
    size_id integer not null
        constraint place_uniforms_size_id_foreign
            references uniform_sizes
                on update cascade on delete cascade,
    constraint place_uniforms_type_id_place_id_used_size_id_unique
        unique (type_id, place_id, used, size_id)
);

create table uniform_courier_relocation_courier_uniform
(
    id bigserial not null
        constraint uniform_courier_relocation_uniform_pkey
            primary key,
    uniform_courier_relocation_id integer not null
        constraint uniform_courier_relocation_uniform_uniform_courier_relocation_i
            references uniform_courier_relocations
                on update cascade on delete cascade,
    created_at timestamp(0),
    updated_at timestamp(0),
    diff integer not null,
    courier_uniform_id integer not null
        constraint uniform_courier_relocation_uniform_courier_uniform_id_foreign
            references courier_uniforms
                on update cascade on delete cascade,
    depremization integer,
    number varchar(255),
    depremization_reason_id integer,
    courier_depremization_id integer
);
create table uniform_courier_relocation_place_uniform
(
    id bigserial not null
        constraint uniform_courier_relocation_place_uniform_pkey
            primary key,
    uniform_courier_relocation_id integer not null
        constraint uniform_courier_relocation_place_uniform_uniform_courier_reloca
            references uniform_courier_relocations
                on update cascade on delete cascade,
    place_uniform_id integer not null
        constraint uniform_courier_relocation_place_uniform_place_uniform_id_forei
            references place_uniforms
                on update cascade on delete cascade,
    created_at timestamp(0),
    updated_at timestamp(0)
);

create table countries
(
    id serial not null
        constraint countries_pkey
            primary key,
    name varchar(255) not null,
    created_at timestamp(0),
    updated_at timestamp(0)
);

create table courier_types
(
    id serial not null
        constraint courier_types_pkey
            primary key,
    name varchar(255) not null
        constraint courier_types_name_unique
            unique,
    description varchar(255) not null,
    created_at timestamp(0),
    updated_at timestamp(0)
);


create table couriers_update_meta
(
    id serial not null primary key,
    sync_ts timestamp without time zone not null,
    in_progress boolean not null,
    created_at timestamp without time zone not null
);

create unique index couriers_update_meta_in_progress_false_unique
    on couriers_update_meta(in_progress)
where
    in_progress is true
;

create index couriers_update_meta_in_progress_created_at
    on couriers_update_meta(in_progress, created_at)
;

create table general_couriers
(
    id serial not null
        constraint general_couriers_pkey
            primary key
        constraint general_couriers_id_foreign
            references couriers,
    vehicle_id integer,
    assign_vehicle_place_id integer
        constraint general_couriers_assign_vehicle_place_id_foreign
            references places,
    assign_vehicle_creator_id integer
        constraint general_couriers_assign_vehicle_creator_id_foreign
            references users,
    vehicle_type varchar(255),
    vehicle_assigned_at timestamp(0),
    created_at timestamp(0),
    updated_at timestamp(0)
);

create table uniform_numbers
(
    id bigserial not null
        constraint uniform_numbers_pkey
            primary key,
    number varchar(255) not null,
    uniform_type_id integer not null
        constraint uniform_numbers_uniform_type_id_foreign
            references uniform_types,
    numberable_id int,
    numberable_type varchar(255),
    created_at timestamp(0),
    updated_at timestamp(0)
);

create table uniform_courier_relocation_courier_uniform_uniform_number
(
    id bigserial not null
        constraint uniform_courier_relocation_courier_uniform_uniform_number_pkey
            primary key,
    uniform_courier_relocation_courier_uniform_id bigint not null
        constraint uniform_courier_relocation_courier_uniform_uniform_number_uniform_courier_relocation_courier_uniform_id_foreign
             references uniform_courier_relocation_courier_uniform,
    uniform_number_id bigint not null
       constraint uniform_foreign
           references uniform_numbers,
    created_at timestamp(0),
    updated_at timestamp(0)
);

commit;
