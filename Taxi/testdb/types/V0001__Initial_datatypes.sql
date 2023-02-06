create type rainbow as enum (
    'red',
    'orange',
    'yellow',
    'green',
    'cyan',
    'blue',
    'violet'
);

create type test_type as (
    id int,
    colour rainbow,
    message text
);
