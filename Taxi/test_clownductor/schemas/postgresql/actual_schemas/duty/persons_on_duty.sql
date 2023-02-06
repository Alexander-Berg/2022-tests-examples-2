create type duty.duty_status_t as enum (
    'in_progress',
    'ended'
);


create table duty.persons_on_duty (
    id text primary key,
    login text not null,
    duty_status duty.duty_status_t not null,
    duty_day date not null,
    ticket text
);

create unique index
    duty_status_in_progress_unique
on
    duty.persons_on_duty (duty_status)
where
    duty_status = 'in_progress'
;

create unique index
    login_duty_day_unique
on
    duty.persons_on_duty (login, duty_day)
;

create unique index
    ticket_unique
on
    duty.persons_on_duty (ticket)
where
    ticket is not null
;
