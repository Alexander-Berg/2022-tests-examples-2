CREATE SCHEMA driver_trackstory;

CREATE TABLE driver_trackstory.archive_dist_locks(
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);

CREATE TABLE driver_trackstory.current_archive_process_hour (
  id BIGINT PRIMARY KEY,
  hour BIGINT
);

CREATE TABLE driver_trackstory.archive_process_tasks(
  partition_num SMALLINT PRIMARY KEY,
  logbroker_offsets JSON,
  time_created TIMESTAMP,
  is_finished BOOLEAN
);

CREATE TABLE driver_trackstory.archive_process_info(
  partition_num SMALLINT PRIMARY KEY,
  hour BIGINT,
  logbroker_offsets JSON,
  work_duration INTERVAL
);
