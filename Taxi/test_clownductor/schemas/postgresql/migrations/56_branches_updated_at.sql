alter table clownductor.branches add column updated_at integer not null default extract(epoch from now());

create function clownductor.set_branch_updated_at() returns trigger as $$
begin
    new.updated_at := extract(epoch from now());
    return new;
end;
$$ language plpgsql;

create trigger set_branch_updated_at_tr
before insert or update on clownductor.branches
for each row
execute procedure clownductor.set_branch_updated_at();
