alter table form_builder.submit_options alter column allow_resend drop not null;
alter table form_builder.submit_options alter column allow_resend drop default;
update form_builder.submit_options set allow_resend = null;

alter table form_builder.partial_submit_options alter column allow_resend drop not null;
alter table form_builder.partial_submit_options alter column allow_resend drop default;
update form_builder.partial_submit_options set allow_resend = null;

drop index form_builder.request_queue_form_code_submit_id_key;
alter table form_builder.request_queue add column allow_resend boolean;
create unique index request_queue_form_code_submit_id_key
    on form_builder.request_queue(form_code, submit_id)
    where allow_resend is false
        and (status = 'PENDING' or status = 'SUBMITTED');

drop index form_builder.partial_request_queue_form_code_stage_num_submit_id_key;
alter table form_builder.partial_request_queue add column allow_resend boolean;
create unique index partial_request_queue_form_code_stage_num_submit_id_key
    on form_builder.partial_request_queue(form_code, stage_num, submit_id)
    where allow_resend is false
        and (status = 'PENDING' or status = 'SUBMITTED');
