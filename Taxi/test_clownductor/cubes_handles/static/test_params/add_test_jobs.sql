insert into task_manager.jobs (
    service_id,
    branch_id,
    name,
    initiator,
    status
)
values (
    1,
    1,
    'DeployNannyServiceNoApprove',
    'deoevgen',
    'canceled'
), (
    1,
    1,
    'ResolveServiceDiff',
    'deoevgen',
    'success'
), (
    2,
    2,
    'ResolveServiceDiff',
    'deoevgen',
    'success'
)
;
