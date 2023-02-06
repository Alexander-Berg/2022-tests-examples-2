create sequence audit_events.audit_events_logs_revision_seq;
alter table audit_events.logs add column revision bigint;
alter sequence audit_events.audit_events_logs_revision_seq owned by audit_events.logs.revision;
create unique index concurrently audit_events_logs_revision on audit_events.logs (revision);
alter table audit_events.logs alter column revision set default nextval('audit_events.audit_events_logs_revision_seq');
alter table audit_events.logs add constraint audit_events_logs_revision_type_not_null check (revision is not null) not valid;
-- after update PG to 12+ version use converter:
-- alter table audit_events.logs alter column revision set not null;
-- alter table audit_events.logs drop constraint audit_events_logs_revision_type_not_null;
-- see: https://habr.com/ru/company/haulmont/blog/493954/
