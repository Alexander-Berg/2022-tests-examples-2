create type balancers.routing_mode_e as enum (
    'round-robin', 'dc-local'
);

alter table balancers.entry_points
    add column routing_mode balancers.routing_mode_e not null default 'round-robin'::balancers.routing_mode_e;
