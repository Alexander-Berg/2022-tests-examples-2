insert into
    perforator.services (tvm_name, clown_id, project_id)
select
    'existed_tvm_service_' || a,
    case
        when mod(a, 2) = 0 then
            null
        else
            a
    end,
    1
from
    generate_series(1, 1001) g(a)
;

insert into
    perforator.services (tvm_name, clown_id, project_id)
select
    'empty_service_' || a,
    null,
    null
from
    generate_series(1, 5) g(a)
;

insert into
    perforator.environments (service_id, tvm_id, env_type)
select
    s.id,
    s.id + 1000,
    'production'
from
    perforator.services s
;

insert into
    perforator.environments (service_id, tvm_id, env_type)
select
    s.id,
    s.id + 1002,
    'testing'
from
    perforator.services s
;

insert into
    perforator.environments (service_id, tvm_id, env_type)
select
    s.id,
    s.id + 1002,
    'unstable'
from
    perforator.services s
;

insert into
    perforator.environment_rules (source_env_id, destination_env_id)
select
    es.id,
    ed.id
from
    perforator.environments es
    join perforator.environments ed
        on es.id = ed.id - 3
        and es.env_type = ed.env_type
;
