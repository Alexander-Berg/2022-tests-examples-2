-- MOBILE MTMISC, BEWARE BEWARE (!!!), mtacs have another mobile, so no DROP SCHEMA or CREATE SCHEMA here

use mobile;

SET NAMES 'utf8';

CREATE TABLE active_apps_cache (
  application_id int(11) unsigned NOT NULL,
  PRIMARY KEY (application_id)
);

CREATE TABLE bundle_ids (
  application_id bigint(20) unsigned NOT NULL,
  operating_system enum('android','ios') NOT NULL,
  bundle_id varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  rows_count bigint unsigned NOT NULL DEFAULT 0,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (application_id, operating_system, bundle_id),
  KEY bundle_ids_bundle_id_key (bundle_id),
  KEY bundle_ids_update_time_key (update_time)
);

CREATE TABLE bundle_ids_store_info (
  operating_system enum('android','ios') NOT NULL,
  bundle_id varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  icon text,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (bundle_id, operating_system),
  KEY bundle_ids_update_time_key (update_time)
);

CREATE TABLE bundle_ids_apps_settings (
   application_id bigint(20) unsigned NOT NULL,
   status enum('enabled','disabled') NOT NULL DEFAULT 'disabled',
   create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (application_id)
);

CREATE TABLE campaigns_log (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  tracking_id bigint(20) unsigned NOT NULL,
  uid bigint(20) unsigned NOT NULL,
  uid_real bigint(20) unsigned NOT NULL,
  action enum('create','edit','archive','restore') NOT NULL,
  timestamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY tracking_id (tracking_id)
);

CREATE TABLE campaigns_recent_metrics (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  tracking_id bigint(20) unsigned NOT NULL,
  installs bigint(20) unsigned NOT NULL,
  clicks bigint(20) unsigned NOT NULL,
  retentions_d1 bigint(20) unsigned NOT NULL,
  retentions_d7 bigint(20) unsigned NOT NULL,
  retentions_d28 bigint(20) unsigned NOT NULL,
  installs_d1 bigint(20) unsigned NOT NULL,
  installs_d7 bigint(20) unsigned NOT NULL,
  installs_d28 bigint(20) unsigned NOT NULL,
  min_data_date date NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY recent_metrics_layer (create_time,tracking_id)
);

CREATE TABLE campaigns_recent_metrics_completed (
  min_data_date date NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (create_time)
);

CREATE TABLE campaigns_stable_metrics (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  tracking_id bigint(20) unsigned NOT NULL,
  installs bigint(20) unsigned NOT NULL,
  clicks bigint(20) unsigned NOT NULL,
  retentions_d1 bigint(20) unsigned NOT NULL,
  retentions_d7 bigint(20) unsigned NOT NULL,
  retentions_d28 bigint(20) unsigned NOT NULL,
  installs_d1 bigint(20) unsigned NOT NULL,
  installs_d7 bigint(20) unsigned NOT NULL,
  installs_d28 bigint(20) unsigned NOT NULL,
  data_date date NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY stable_metrics_layer (data_date,tracking_id)
);

CREATE TABLE campaigns_stable_metrics_completed (
  data_date date NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (data_date)
);

CREATE TABLE event_names_cache (
  application_id bigint(20) unsigned NOT NULL,
  event_name text NOT NULL,
  last_occurrence datetime NOT NULL,
  PRIMARY KEY (application_id,event_name(255))
);

CREATE TABLE event_names_cache_meta (
  last_cached_date date NOT NULL,
  PRIMARY KEY (last_cached_date)
);

CREATE TABLE event_names_cache_settings (
  application_id int(11) unsigned NOT NULL,
  cache_disabled tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (application_id)
);

CREATE TABLE properties (
  name varchar(100) NOT NULL DEFAULT '',
  value varchar(100) DEFAULT NULL,
  PRIMARY KEY (name)
);

CREATE TABLE push_campaigns_for_abort (
  campaign_id bigint(20) unsigned NOT NULL,
  PRIMARY KEY (campaign_id)
);

CREATE TABLE push_campaigns_onetime_start_locks (
  campaign_id bigint(20) unsigned NOT NULL,
  request_id char(36) NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY campaign_start (campaign_id)
);

CREATE TABLE push_campaigns_processing (
  campaign_id bigint(20) unsigned NOT NULL,
  queue varchar(255) NOT NULL,
  messages_count bigint(20) NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (campaign_id,queue),
  KEY update_time (update_time)
);

CREATE TABLE push_campaigns_tz_start_locks (
  campaign_id bigint(20) unsigned NOT NULL,
  utc_offset bigint(20) NOT NULL,
  request_id char(36) NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY campaign_start (campaign_id,utc_offset)
);

CREATE TABLE push_groups (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  uid bigint(20) unsigned NOT NULL DEFAULT '0',
  application_id bigint(20) unsigned NOT NULL,
  name varchar(255) NOT NULL,
  status enum('active','deleted') NOT NULL DEFAULT 'active',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  send_rate mediumint(9) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY application_id (application_id,status)
);

CREATE TABLE push_ping_send_rates_settings (
  application_id bigint(20) unsigned NOT NULL,
  send_rate mediumint(9) unsigned DEFAULT NULL,
  comment varchar(255) DEFAULT NULL,
  PRIMARY KEY (application_id)
);

CREATE TABLE push_transfers (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  group_id bigint(20) unsigned NOT NULL,
  client_transfer_id bigint(20) unsigned DEFAULT NULL,
  tag varchar(255) NOT NULL,
  status enum('pending','in_progress','sent','failed') NOT NULL DEFAULT 'pending',
  log_expired tinyint(1) NOT NULL DEFAULT '0',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY client_transfer_id (group_id,client_transfer_id),
  KEY update_time (update_time)
);

CREATE TABLE push_transfers_batch (
  batch_id bigint(20) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (batch_id)
);

CREATE TABLE push_transfers_batch_content (
  batch_id bigint(20) DEFAULT NULL,
  transfer_id bigint(20) DEFAULT NULL,
  UNIQUE KEY batch_transfer (batch_id,transfer_id),
  KEY transfer_id (transfer_id)
);

CREATE TABLE push_transfers_failures (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  transfer_id bigint(20) unsigned NOT NULL,
  error_type varchar(255) NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE push_transfers_failures_params (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  failure_id bigint(20) unsigned NOT NULL,
  param_key varchar(255) NOT NULL,
  param_value text NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY failure_id (failure_id,param_key)
);

CREATE TABLE push_transfers_processing (
  transfer_id bigint(20) unsigned NOT NULL,
  queue varchar(255) NOT NULL,
  messages_count bigint(20) NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (transfer_id,queue),
  KEY update_time (update_time)
);

CREATE TABLE timezones_gathering_meta (
  last_check_date_iso varchar(255) NOT NULL,
  PRIMARY KEY (last_check_date_iso)
);

CREATE TABLE tokens_shuffled_ping_task_log (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  application_id bigint(20) unsigned NOT NULL,
  devices bigint(20) unsigned NOT NULL,
  send_rate mediumint(9) unsigned DEFAULT NULL,
  launched tinyint(1) NOT NULL DEFAULT '1',
  include_android tinyint(1) NOT NULL DEFAULT '1',
  include_ios tinyint(1) NOT NULL DEFAULT '1',
  start_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE tokens_shuffled_ping_task_meta (
  executions mediumint(9) unsigned NOT NULL DEFAULT '0',
  prime_hash_number mediumint(9) NOT NULL DEFAULT '0',
  ring_size_android mediumint(9) NOT NULL DEFAULT '0',
  ring_size_ios mediumint(9) NOT NULL DEFAULT '0',
  comment text
);

CREATE TABLE used_profiles_attributes_cache (
  application_id int(10) unsigned NOT NULL,
  attribute_id bigint(20) NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY used_profile_item (application_id,attribute_id)
);

CREATE TABLE apple_app_ids (
  apple_app_id bigint(20) unsigned NOT NULL,
  bundle_id varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (apple_app_id,bundle_id),
  KEY apple_app_ids_bundle_id_key (bundle_id)
);
