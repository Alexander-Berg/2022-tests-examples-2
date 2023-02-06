start transaction;

alter table clownductor.projects add column deleted_at integer default null;

commit;
