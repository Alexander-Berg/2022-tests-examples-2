insert into
    task_processor.providers
    (name, tvm_id, hostname, tvm_name, updated_at)
values
    ('clownductor', 1234, '$mockserver/provider-client', 'clownductor', extract (epoch from now()));

