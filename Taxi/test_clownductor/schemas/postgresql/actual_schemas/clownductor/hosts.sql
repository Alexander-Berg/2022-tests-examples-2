create table clownductor.hosts (
    -- fqdn of the host
    name text not null unique primary key,
    -- part of what branch this host is
    branch_id integer references
        clownductor.branches (id) on delete cascade,
    -- datacenter name
    datacenter text not null,
    -- parent host if it is virtual machine
    dom0_name text default null,
    -- when dom0 was determined
    dom0_updated_at integer default null
);

create index clownductor_hosts_dom0_name
    on clownductor.hosts (dom0_name);
create index clownductor_hosts_datacenter
    on clownductor.hosts (datacenter);
create index clownductor_hosts_branch_id
    on clownductor.hosts (branch_id);
