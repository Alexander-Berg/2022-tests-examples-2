start transaction;

drop index task_processor.task_processor_idempotency_token;

create unique index task_processor_idempotency_token
    on task_processor.jobs (idempotency_token);

commit;
