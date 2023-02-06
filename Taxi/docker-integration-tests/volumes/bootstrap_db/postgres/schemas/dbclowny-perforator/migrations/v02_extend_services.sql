alter table perforator.services drop constraint if exists services_clown_id_key;
alter table perforator.services add column project_id bigint;
