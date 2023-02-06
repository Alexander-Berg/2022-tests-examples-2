insert into task_manager.jobs (
    service_id,
    branch_id,
    name,
    initiator,
    status
)
values
    (
        1,
        1,
        'DeployNannyServiceNoApprove',
        'deoevgen',
        'canceled'
    ),
    (
        1,
        2,
        'DeployNannyServiceNoApprove',
        'deoevgen',
        'in_progress'
    ),
    (
        1,
        3,
        'DeployNannyServiceWithApprove',
        'deoevgen',
        'in_progress'
    );

insert into task_manager.job_variables (
    job_id,
    variables
)
values
    (
        1,
        '{"name": "DeployNannyServiceNoApprove", "image": "image_name", "comment": "test comment", "sandbox_resources": null}'
    ),
    (
        2,
        '{"name": "DeployNannyServiceNoApprove", "image": "image_name", "comment": "test comment", "sandbox_resources": null}'
    ),
    (
        3,
        '{"name": "DeployNannyServiceWithApprove", "image": "image_name", "comment": "test comment", "prestable_name": "prestabe_name_test", "release_ticket_st": "release_ticket_st", "approving_managers": [], "approving_developers": [], "sandbox_resources": null}'
    );
