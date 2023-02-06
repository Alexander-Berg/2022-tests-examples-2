alter table form_builder.request_queue
    add column form_code text references form_builder.forms(code) on delete cascade,
    add column submit_id text;

alter table form_builder.submit_options
    add column allow_resend boolean not null default false;

alter table form_builder.partial_submit_options
    add column allow_resend boolean not null default false;

create unique index request_queue_form_code_submit_id_key
    on form_builder.request_queue(form_code, submit_id)
    where status = 'PENDING' or status = 'SUBMITTED';
