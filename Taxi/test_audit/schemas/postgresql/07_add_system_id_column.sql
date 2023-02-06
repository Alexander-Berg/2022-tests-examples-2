start transaction;

alter table audit_events.actions add system_id integer references audit_events.systems (id);
alter table audit_events.actions drop constraint actions_action_key;
drop index if exists actions_action_key;
create unique index actions_action_system_id_unique on audit_events.actions (action, system_id);

commit;
