-- MOBILE

drop schema if exists mobile;

create schema mobile collate utf8_general_ci;

use mobile;

SET NAMES 'utf8';

CREATE TABLE agency_accounts (
  partner_id bigint(20) unsigned NOT NULL,
  user_login varchar(255) NOT NULL,
  PRIMARY KEY (partner_id,user_login)
);

CREATE TABLE agency_events (
  obj_id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  application_id bigint(20) unsigned NOT NULL,
  event_label mediumtext NOT NULL,
  event_label_hash char(36) NOT NULL,
  PRIMARY KEY (obj_id),
  UNIQUE KEY application_id (application_id,event_label_hash)
);

CREATE TABLE agency_partners (
  obj_id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  application_id bigint(20) unsigned NOT NULL,
  partner_id bigint(20) unsigned NOT NULL,
  PRIMARY KEY (obj_id),
  UNIQUE KEY application_id (application_id,partner_id)
);

CREATE TABLE android_push_credentials (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  application_id bigint(20) unsigned NOT NULL,
  auth_key varchar(255) NOT NULL,
  valid tinyint(1) NOT NULL DEFAULT '1',
  version bigint(20) unsigned NOT NULL DEFAULT '0',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY application_id (application_id)
);

CREATE TABLE apple_push_credentials (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  application_id bigint(20) unsigned NOT NULL,
  cert blob NOT NULL,
  password varchar(255) NOT NULL,
  expiration_utc_time datetime DEFAULT NULL,
  type enum('production','development') NOT NULL,
  valid tinyint(1) NOT NULL DEFAULT '1',
  version bigint(20) unsigned NOT NULL DEFAULT '0',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY application_id (application_id,type)
);

CREATE TABLE apple_team_ids (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  application_id bigint(20) unsigned NOT NULL,
  apple_team_id varbinary(255) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY application_id (application_id)
);

CREATE TABLE application_categories (
  id int(11) unsigned NOT NULL AUTO_INCREMENT,
  name_en varchar(255) NOT NULL,
  name_ru varchar(255) NOT NULL,
  type enum('common','game') NOT NULL DEFAULT 'common',
  PRIMARY KEY (id),
  UNIQUE KEY name_type_en (name_en,type),
  UNIQUE KEY name_type_ru (name_ru,type)
);

CREATE TABLE applications(
  id                               int(11) unsigned NOT NULL AUTO_INCREMENT,
  uid                              bigint(20) unsigned NOT NULL,
  status                           enum('active','deleted') NOT NULL DEFAULT 'active',
  name                             varchar(255) NOT NULL,
  category                         int(11) unsigned DEFAULT NULL,
  time_zone_id                     int(11) unsigned NOT NULL DEFAULT '1',
  api_key_128                      char(36)              DEFAULT NULL,
  import_token                     char(36)              DEFAULT '',
  create_time                      datetime              DEFAULT CURRENT_TIMESTAMP,
  update_time                      timestamp    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  layer_id                         int(10) unsigned NOT NULL DEFAULT '2',
  rows_count                       bigint(20) unsigned NOT NULL DEFAULT '0',
  hide_address                     tinyint(1) NOT NULL DEFAULT '0',
  gdpr_agreement_accepted          tinyint(1) NOT NULL DEFAULT '0',
  is_installation_tracking_enabled tinyint(1) NOT NULL DEFAULT '1',
  attribution_model                enum('last_click','prefer_yandex') NOT NULL,
  is_profiles_collecting_enabled   tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (id),
  UNIQUE KEY unique_import_token (import_token),
  KEY                              uid (uid)
);

CREATE TABLE application_icons (
  application_id int unsigned NOT NULL,
  icon text,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (application_id)
);

CREATE TABLE application_features
(
    id bigint unsigned NOT NULL AUTO_INCREMENT,
    application_id int(11) unsigned NOT NULL,
    feature_name enum('lib', 'app_with_shared_bundles', 'skad_manual_enabled', 'ios') NOT NULL,
    update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY application_features_app_feature(application_id,feature_name),
    KEY application_features_name(feature_name)
);

CREATE TABLE applications_limit
(
    uid        bigint(20) unsigned NOT NULL,
    apps_limit bigint(20) unsigned NOT NULL,
    PRIMARY KEY (uid)
);

CREATE TABLE campaigns
(
  tracking_id bigint(20) unsigned NOT NULL,
  api_key int(10) unsigned NOT NULL,
  NAME varchar(512) NOT NULL,
  STATUS enum('Active','Deleted') NOT NULL DEFAULT 'Active',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  attribution_window_strict_seconds int(10) unsigned DEFAULT '864000',
  attribution_window_fingerprint_seconds int(10) unsigned DEFAULT '86400',
  reattribution_enabled tinyint(1) NOT NULL DEFAULT '0',
  remarketing_enabled tinyint(1) NOT NULL DEFAULT '0',
  remarketing_inactive_period bigint(20) unsigned NOT NULL DEFAULT '0',
  remarketing_send_postbacks_to_install_partner tinyint(1) NOT NULL DEFAULT '0',
  remarketing_with_smartlinks tinyint(1) NOT NULL DEFAULT '0',
  custom_params varchar(4096) DEFAULT NULL,
  partner_id bigint(20) NOT NULL DEFAULT '0',
  adwords_conversion_id varchar(255) DEFAULT NULL,
  adwords_conversion_label varchar(255) DEFAULT NULL,
  adwords_link_id varchar(255) DEFAULT NULL,
  doubleclick_src varchar(255) DEFAULT NULL,
  doubleclick_cat varchar(255) DEFAULT NULL,
  doubleclick_type varchar(255) DEFAULT NULL,
  doubleclick_authorization_token varchar(255) DEFAULT NULL,
  facebook_decryption_key varchar(255) DEFAULT NULL,
  tiktok_app_id varchar(255) DEFAULT NULL,
  huawei_link_id varchar(255) DEFAULT NULL,
  apple_search_campaign_id varchar(255) DEFAULT NULL,
  direct_campaign_id bigint unsigned DEFAULT NULL,
  source enum('appmetrica','direct_uac') NOT NULL DEFAULT 'appmetrica',
  PRIMARY KEY (tracking_id),
  UNIQUE KEY apple_search_campaign_id_idx (apple_search_campaign_id),
  KEY ix_api_key (api_key) USING HASH,
  KEY partner_id_idx (partner_id),
  KEY campaigns_updtime_idx (update_time)
);

CREATE TABLE clids_to_campaigns (
  application_id bigint(20) unsigned NOT NULL,
  clid_name varbinary(255) NOT NULL,
  clid_value bigint(20) unsigned NOT NULL,
  tracking_id bigint(20) unsigned NOT NULL,
  PRIMARY KEY (application_id,clid_name,clid_value)
);

CREATE TABLE clusters (
  application_id bigint(20) unsigned NOT NULL,
  cluster enum('mtgiga','mtmobgiga') NOT NULL DEFAULT 'mtgiga',
  status enum('enabled','disabled') NOT NULL DEFAULT 'enabled',
  PRIMARY KEY (application_id,cluster)
);

CREATE TABLE crash_comments (
  apikey int(10) unsigned NOT NULL,
  owner bigint(20) NOT NULL,
  crash_id bigint(20) unsigned NOT NULL DEFAULT '0',
  message varchar(2048) NOT NULL,
  status enum('active','deleted') NOT NULL DEFAULT 'active',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (apikey,crash_id)
);

CREATE TABLE deep_links (
  id bigint(20) NOT NULL AUTO_INCREMENT,
  apikey int(10) unsigned NOT NULL,
  link varchar(4096) NOT NULL,
  title varchar(512) DEFAULT NULL,
  platform varchar(128) NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  status enum('active','deleted') DEFAULT 'active',
  PRIMARY KEY (id),
  KEY apikey (apikey,status)
);

CREATE TABLE device_models (
  original_model varchar(255) NOT NULL,
  model varchar(255) NOT NULL,
  PRIMARY KEY (original_model)
);

CREATE TABLE device_timezones (
  application_id bigint(20) unsigned NOT NULL,
  offset_seconds bigint(20) NOT NULL,
  PRIMARY KEY (application_id,offset_seconds),
  KEY application_id (application_id)
);

CREATE TABLE dismissed_notifications (
  uid bigint(20) NOT NULL,
  notification_id bigint(20) NOT NULL,
  PRIMARY KEY (uid,notification_id)
);

CREATE TABLE ecommerce_convert_rules (
  rule_id bigint(20) NOT NULL AUTO_INCREMENT,
  application_id int(10) unsigned NOT NULL,
  event_type tinyint(3) unsigned NOT NULL,
  event_name text,
  yandex_direct_application_id bigint(20) unsigned DEFAULT NULL,
  ecommerce_event_type tinyint(3) unsigned DEFAULT NULL,
  metrika_counter_id int(10) unsigned NOT NULL,
  skuid_json_path text,
  revenue_json_path text,
  origin enum('core','interface') NOT NULL DEFAULT 'core',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (rule_id),
  KEY application_id_key (application_id)
);

CREATE TABLE event_comments (
  application_id int(10) unsigned NOT NULL,
  event_name text NOT NULL,
  comment varchar(2048) DEFAULT NULL,
  owner_uid bigint(20) NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY application_id (application_id)
);

CREATE TABLE event_filters (
  id int(10) unsigned NOT NULL AUTO_INCREMENT,
  application_id int(10) unsigned NOT NULL,
  sample float NOT NULL DEFAULT '1',
  app_version_name_lower_bound text,
  app_version_name_upper_bound text,
  event_type tinyint(3) unsigned NOT NULL,
  event_name text,
  exclude_event_name text,
  application_ids text,
  exclude_application_ids text,
  action enum('invalidate','convert_to_event_statbox','disable_deduplication','drop') DEFAULT NULL,
  status enum('active','inactive') NOT NULL DEFAULT 'active',
  create_time datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  origin enum('interface','core') NOT NULL DEFAULT 'core',
  PRIMARY KEY (id),
  KEY application_id (application_id)
);

CREATE TABLE funnels (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  app_id int(10) unsigned NOT NULL,
  owner bigint(20) NOT NULL,
  name varchar(255) NOT NULL,
  comment mediumtext,
  pattern_type enum('user','session') NOT NULL,
  pattern mediumtext,
  frontend_pattern mediumtext,
  status enum('active','deleted') NOT NULL DEFAULT 'active',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY funnels_app_id_status (app_id,status)
);

CREATE TABLE huawei_push_credentials (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  application_id bigint(20) unsigned NOT NULL,
  client_id varchar(255) NOT NULL,
  client_secret varchar(255) NOT NULL,
  valid tinyint(1) NOT NULL DEFAULT '1',
  version bigint(20) unsigned NOT NULL DEFAULT '0',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY application_id (application_id)
);

CREATE TABLE icons (
  id bigint(20) NOT NULL AUTO_INCREMENT,
  duri varchar(8192) DEFAULT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE ios_libraries (
  library varchar(256) NOT NULL
);

CREATE TABLE labels (
  id int(10) unsigned NOT NULL AUTO_INCREMENT,
  uid bigint(20) unsigned NOT NULL,
  label varchar(255) NOT NULL,
  status enum('active','deleted') NOT NULL DEFAULT 'active',
  PRIMARY KEY (id),
  KEY uid (uid)
);

CREATE TABLE layers_config (
  layer_id int(3) unsigned NOT NULL DEFAULT '0',
  weight int(3) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (layer_id)
);

CREATE TABLE location_settings (
  application_id int(11) unsigned NOT NULL,
  ignore_location_enabled tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (application_id)
);

CREATE TABLE monotone_seq (
  seq varchar(64) NOT NULL,
  epoch bigint(20) unsigned DEFAULT NULL,
  counter int(11) DEFAULT NULL,
  PRIMARY KEY (seq)
);

CREATE TABLE multiplatform_campaigns (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  tracking_id bigint(20) unsigned NOT NULL,
  platform varchar(128) DEFAULT NULL,
  target_url_id bigint(20) unsigned DEFAULT NULL,
  deep_link_id bigint(20) unsigned DEFAULT NULL,
  postclick_url varchar(1024) DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY campaign_by_platform (tracking_id,platform)
);

CREATE TABLE notification_emails (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  application_id bigint(20) unsigned NOT NULL,
  email varchar(256) DEFAULT NULL,
  update_uid bigint(20) unsigned NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY emails_application (application_id)
);

CREATE TABLE notification_localizations (
  notification_id bigint(20) NOT NULL,
  language char(2) NOT NULL,
  title varchar(4096) DEFAULT NULL,
  body varchar(4096) DEFAULT NULL,
  PRIMARY KEY (notification_id,language)
);

CREATE TABLE notifications (
  id bigint(20) NOT NULL AUTO_INCREMENT,
  type enum('info','update','critical') NOT NULL,
  alert tinyint(1) DEFAULT NULL,
  pending tinyint(1) DEFAULT NULL,
  start_time datetime NOT NULL,
  end_time datetime NOT NULL,
  icon_id bigint(20) DEFAULT NULL,
  status enum('active','deleted') NOT NULL DEFAULT 'active',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  uid bigint(20) NOT NULL DEFAULT '0',
  uids mediumtext,
  obj_ids mediumtext,
  PRIMARY KEY (id),
  KEY start_time (start_time,end_time)
);

CREATE TABLE notifications_scopes (
  notification_id bigint(20) NOT NULL,
  scope_id bigint(20) NOT NULL,
  PRIMARY KEY (notification_id,scope_id)
);

CREATE TABLE omni_postbacks (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  ignore_partner_id bigint(20) unsigned DEFAULT NULL,
  status enum('active','deleted') NOT NULL,
  kind enum('cpi','cpa') NOT NULL DEFAULT 'cpi',
  event_name text,
  url mediumtext NOT NULL,
  method enum('GET','POST') NOT NULL DEFAULT 'GET',
  headers text NOT NULL,
  body text NOT NULL,
  platform enum('android','iOS','WindowsPhone') DEFAULT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  event_type tinyint(3) unsigned NOT NULL DEFAULT '4',
  event_subtype int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE omni_postbacks_integrations (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  application_id bigint(20) unsigned NOT NULL,
  tracking_id bigint(20) unsigned DEFAULT NULL,
  omni_postback_id bigint(20) unsigned NOT NULL,
  status enum('active','deleted') NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY application_id (application_id,omni_postback_id),
  KEY postback_id (omni_postback_id),
  KEY tracking_id (tracking_id)
);

CREATE TABLE organic_sources (
  id bigint(20) unsigned NOT NULL,
  tracking_id bigint(20) unsigned NOT NULL,
  referrer varchar(256) NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE packages_ids (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  application_id bigint(20) unsigned NOT NULL,
  platform enum('android','iOS','WindowsPhone') NOT NULL,
  package_id varbinary(255) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY application_id (application_id)
);

CREATE TABLE postback_templates (
  id bigint(20) NOT NULL AUTO_INCREMENT,
  uid bigint(20) DEFAULT NULL,
  partner_id bigint(20) NOT NULL,
  url varchar(4096) NOT NULL,
  method enum('GET','POST') NOT NULL DEFAULT 'GET',
  headers text,
  body text,
  kind enum('cpi','cpr','cpa') NOT NULL DEFAULT 'cpi',
  title varchar(512) DEFAULT NULL,
  mandatory tinyint(1) NOT NULL DEFAULT '0',
  event_name varchar(1024) DEFAULT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  status enum('active','deleted') DEFAULT 'active',
  description_key varchar(1024) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY uid (uid,partner_id,status)
);

CREATE TABLE postbacks (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  tracking_id bigint(20) unsigned NOT NULL,
  url text NOT NULL,
  method enum('GET','POST') NOT NULL DEFAULT 'GET',
  headers text NOT NULL,
  body text NOT NULL,
  kind enum('cpi','cpr','cpa','cppi') NOT NULL DEFAULT 'cpi',
  event_name varchar(1024) DEFAULT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  once_per_installation tinyint(1) NOT NULL DEFAULT '0',
  attribution_window bigint(20) unsigned DEFAULT NULL,
  mandatory tinyint(1) NOT NULL DEFAULT '0',
  event_type tinyint(3) unsigned NOT NULL DEFAULT '4',
  event_subtype int(10) unsigned DEFAULT NULL,
  conversion_id bigint unsigned,
  PRIMARY KEY (id),
  KEY tracking_id_index (tracking_id)
);

CREATE TABLE conversions (
  id bigint unsigned NOT NULL AUTO_INCREMENT,
  name varchar(255) NOT NULL,
  application_id bigint unsigned NOT NULL,
  event_type tinyint unsigned NOT NULL DEFAULT '4',
  event_subtype int unsigned DEFAULT NULL,
  event_name varchar(1024) DEFAULT NULL,
  attribution_rule enum('any','first') NOT NULL DEFAULT 'any',
  attribution_window bigint unsigned DEFAULT NULL,
  origin enum('appmetrica','direct') NOT NULL DEFAULT 'appmetrica',
  direct_goal_id bigint unsigned,
  direct_bundle_id varchar(255),
  direct_platform varchar(255),
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY application_id_index (application_id),
  UNIQUE KEY uniq_direct_goal_id (direct_goal_id)
);

CREATE TABLE predefined_profile_attributes_meta (
  attribute_id bigint(20) NOT NULL,
  external_name varchar(255) NOT NULL,
  sdk_method varchar(255) NOT NULL,
  PRIMARY KEY (attribute_id)
);

CREATE TABLE profile_attributes (
  id bigint(20) NOT NULL AUTO_INCREMENT,
  application_id int(10) unsigned DEFAULT NULL,
  name varchar(255) NOT NULL,
  type enum('string','number','bool','counter','price') NOT NULL,
  status enum('active','deleted') NOT NULL DEFAULT 'active',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  class enum('user','predefined','system') NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY profile_item (application_id,name,type)
);

CREATE TABLE push_campaign_failures (
  id bigint(20) unsigned NOT NULL,
  stack_trace text NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE push_campaigns (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  version bigint(20) unsigned NOT NULL DEFAULT '0',
  owner_uid bigint(20) unsigned NOT NULL,
  name varchar(255) NOT NULL,
  application_id bigint(20) unsigned NOT NULL,
  status enum('new','pending','in_progress','aborted','failed','sent','deleted') NOT NULL DEFAULT 'new',
  status_unarchived enum('new','pending','in_progress','aborted','failed','sent') DEFAULT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  filter_expression mediumtext,
  filter_params mediumtext,
  filter_params_v2 mediumtext,
  date1 varchar(255) NOT NULL,
  date2 varchar(255) NOT NULL,
  send_time_policy enum('now','delayed') NOT NULL,
  send_time datetime DEFAULT NULL,
  send_time_local varchar(255) DEFAULT NULL,
  send_time_zoned varchar(255) DEFAULT NULL,
  use_timezone enum('application','device') DEFAULT NULL,
  send_rate mediumint(9) DEFAULT NULL,
  fail_reason varchar(255) DEFAULT NULL,
  silent tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (id)
);

CREATE TABLE push_campaigns_estimations (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  application_id bigint(20) unsigned NOT NULL,
  segment_hash bigint(20) NOT NULL,
  status enum('running','ready','failed') NOT NULL DEFAULT 'running',
  accuracy float(6,5) NOT NULL DEFAULT '0.00000',
  total_uniqs bigint(20) unsigned NOT NULL DEFAULT '0',
  total_uniqs_including_dead_push_tokens bigint(20) unsigned DEFAULT '0',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE push_campaigns_estimations_by_lang (
  estimation_id bigint(20) unsigned NOT NULL,
  lang varchar(5) NOT NULL,
  uniqs bigint(20) unsigned NOT NULL,
  PRIMARY KEY (estimation_id,lang)
);

CREATE TABLE push_campaigns_estimations_by_platform (
  estimation_id bigint(20) unsigned NOT NULL,
  platform enum('android','iOS','WindowsPhone') NOT NULL,
  uniqs bigint(20) unsigned NOT NULL,
  PRIMARY KEY (estimation_id,platform)
);

CREATE TABLE push_campaigns_start_schedule (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  correlation_id char(36) NOT NULL,
  campaign_id bigint(20) unsigned NOT NULL,
  start_time datetime NOT NULL,
  type enum('onetime','fixed_tz') NOT NULL,
  utc_offset bigint(20) DEFAULT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  status enum('active','processed') NOT NULL DEFAULT 'active',
  campaign_start_time timestamp NULL DEFAULT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE push_hypotheses (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  campaign_id bigint(20) unsigned NOT NULL,
  name varchar(255) NOT NULL,
  type enum('alternative','zero') NOT NULL,
  devices_share decimal(6,5) DEFAULT NULL,
  `order` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (id),
  KEY campaign_id (campaign_id)
);

CREATE TABLE push_messages (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  hypothesis_id bigint(20) unsigned NOT NULL,
  app_platform enum('android','iOS','WindowsPhone') NOT NULL,
  locale varchar(5) NOT NULL,
  is_default tinyint(1) NOT NULL,
  android_title mediumtext,
  android_text mediumtext,
  android_icon tinytext,
  android_icon_background int(11) DEFAULT NULL,
  android_image tinytext,
  android_banner tinytext,
  android_data mediumtext,
  android_sound tinytext,
  android_vibration tinytext,
  android_led_color int(11) DEFAULT NULL,
  android_led_interval int(11) DEFAULT NULL,
  android_led_pause_interval int(11) DEFAULT NULL,
  android_priority int(11) DEFAULT NULL,
  android_visibility int(11) DEFAULT NULL,
  android_urgency enum('normal','high') DEFAULT 'high',
  android_collapse_key int(11) DEFAULT NULL,
  android_channel_id text,
  android_time_to_live int(11) DEFAULT NULL,
  android_time_to_live_on_device int(11) DEFAULT NULL,
  apple_title mediumtext,
  apple_text mediumtext,
  apple_badge tinytext,
  apple_expiration tinytext,
  apple_priority tinyint(4) NOT NULL DEFAULT '10',
  apple_data mediumtext,
  apple_sound tinytext,
  apple_mutable_content int(11) NOT NULL DEFAULT '1',
  apple_category text,
  apple_thread_id text,
  apple_collapse_id varchar(1024) DEFAULT NULL,
  winphone_title mediumtext,
  winphone_text mediumtext,
  action_type enum('open_app','url','deeplink') NOT NULL,
  open_url mediumtext,
  open_deeplink_id bigint(20) DEFAULT NULL,
  mpns_target_page varchar(255) DEFAULT NULL,
  enabled tinyint(1) NOT NULL,
  PRIMARY KEY (id),
  KEY hypothesis_id (hypothesis_id)
);

CREATE TABLE push_tokens_ping (
  application_id bigint(20) unsigned NOT NULL,
  status enum('enabled','disabled') NOT NULL DEFAULT 'enabled',
  PRIMARY KEY (application_id)
);

CREATE TABLE revenue_android_credentials (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  application_id bigint(20) unsigned NOT NULL,
  verification_enabled tinyint(1) unsigned NOT NULL DEFAULT '0',
  public_key text,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY app_id (application_id)
);

CREATE TABLE revenue_apple_credentials (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  application_id bigint(20) unsigned NOT NULL,
  verification_enabled tinyint(1) unsigned NOT NULL DEFAULT '0',
  shared_secret text,
  environment enum('production','testing') NOT NULL DEFAULT 'production',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY app_id_env (application_id,environment)
);

CREATE TABLE segments (
  segment_id int(10) unsigned NOT NULL AUTO_INCREMENT,
  apikey int(10) unsigned NOT NULL,
  owner bigint(20) NOT NULL,
  name varchar(255) NOT NULL,
  params mediumtext,
  expression mediumtext,
  status enum('active','deleted') NOT NULL DEFAULT 'active',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  params_v2 mediumtext,
  PRIMARY KEY (segment_id),
  KEY apikey (apikey)
);

CREATE TABLE special_partner_types (
  partner_id bigint(20) NOT NULL,
  type varchar(255) NOT NULL,
  PRIMARY KEY (partner_id)
);

CREATE TABLE target_urls (
  id bigint(20) NOT NULL AUTO_INCREMENT,
  apikey int(10) unsigned NOT NULL,
  url varchar(4096) NOT NULL,
  title varchar(512) DEFAULT NULL,
  platform varchar(128) DEFAULT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  status enum('active','deleted') DEFAULT 'active',
  PRIMARY KEY (id),
  KEY apikey (apikey,status)
);

CREATE TABLE test_devices (
  id bigint(20) NOT NULL AUTO_INCREMENT,
  uid bigint(20) NOT NULL,
  device_id varchar(8192) NOT NULL,
  app_id int(10) unsigned NOT NULL,
  name varchar(4096) NOT NULL,
  type enum('ios_ifa','google_aid','windows_aid','huawei_oaid') NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  status enum('active','deleted') NOT NULL DEFAULT 'active',
  purpose enum('reattribution','push_notifications') NOT NULL DEFAULT 'reattribution',
  PRIMARY KEY (id),
  KEY app_id (app_id)
);

CREATE TABLE third_party_campaigns (
  adwords_conversion_id varchar(255) NOT NULL,
  adwords_conversion_label varchar(255) NOT NULL,
  adwords_campaign_id varchar(255) NOT NULL,
  PRIMARY KEY (adwords_conversion_id,adwords_conversion_label,adwords_campaign_id)
);

CREATE TABLE tracking_partners (
  pub_id bigint(20) NOT NULL AUTO_INCREMENT,
  partner_name varchar(4096) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  postback_url varchar(4096) DEFAULT NULL,
  STATUS enum('Active','Inactive') NOT NULL DEFAULT 'Active',
  uid bigint(20) DEFAULT NULL,
  icon_url varchar(1024) DEFAULT NULL,
  website_url varchar(1024) DEFAULT NULL,
  priority int(11) NOT NULL DEFAULT '0',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (pub_id),
  KEY pub_id (pub_id),
  KEY partner_uid_idx (uid),
  KEY partner_prior_idx (priority)
);

CREATE TABLE tracking_url_macros (
  id bigint(20) NOT NULL AUTO_INCREMENT,
  partner_id bigint(20) NOT NULL,
  url_param varchar(512) NOT NULL,
  macro varchar(512) NOT NULL,
  comment varchar(4096) DEFAULT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  status enum('active','deleted') DEFAULT 'active',
  platform varchar(128) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY partner_id (partner_id)
);

CREATE TABLE use_universal_links (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  application_id bigint(20) unsigned NOT NULL,
  use_universal_links tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (id),
  UNIQUE KEY application_id2 (application_id)
);

CREATE TABLE user_labels (
  uid bigint(20) unsigned NOT NULL,
  apikey int(10) unsigned NOT NULL,
  label_id int(10) unsigned NOT NULL,
  PRIMARY KEY (uid,apikey)
);

CREATE TABLE windows_push_credentials (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  application_id bigint(20) unsigned NOT NULL,
  package_security_identifier varchar(255) NOT NULL,
  secret_key varchar(255) NOT NULL,
  valid tinyint(1) NOT NULL DEFAULT '1',
  version bigint(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (id),
  UNIQUE KEY application_id (application_id)
);

CREATE TABLE skad_cv_config (
  config_id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  application_id bigint(20) unsigned NOT NULL,
  type enum('not_configured','conversion','revenue','engagement') NOT NULL,
  max_measurement_time_seconds int(10) unsigned DEFAULT NULL,
  max_measurement_time_interface_unit enum('minutes','hours','days') DEFAULT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (config_id),
  UNIQUE KEY skad_cv_config_application_id_key (application_id),
  KEY skad_cv_config_update_time (update_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE skad_cv_config_archive (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  config_id bigint(20) unsigned NOT NULL,
  application_id bigint(20) unsigned NOT NULL,
  value text NOT NULL,
  create_time timestamp NOT NULL,
  remove_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE skad_cv_config_bundle_ids (
  config_id bigint(20) unsigned NOT NULL,
  bundle_id varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (bundle_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE skad_cv_config_conversion (
  config_id bigint(20) unsigned NOT NULL,
  position int(10) unsigned NOT NULL,
  event_type tinyint(3) unsigned NOT NULL,
  event_name varchar(512) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  event_subtype int(10) unsigned DEFAULT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (config_id,position),
  UNIQUE KEY skad_cv_config_client_events_key (config_id,event_type,event_name),
  UNIQUE KEY skad_cv_config_subtype_events_key (config_id,event_type,event_subtype)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE skad_cv_config_engagement (
  config_id bigint(20) unsigned NOT NULL,
  event_type tinyint(3) unsigned NOT NULL,
  event_name varchar(512) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  event_subtype int(10) unsigned DEFAULT NULL,
  minimum int(10) unsigned NOT NULL,
  step_size int(10) unsigned NOT NULL,
  step_count int(10) unsigned NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (config_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE skad_cv_config_revenue (
  config_id bigint(20) unsigned NOT NULL,
  event_type tinyint(3) unsigned NOT NULL,
  event_subtype int(10) unsigned DEFAULT NULL,
  currency_code char(3) NOT NULL,
  minimum decimal(15,6) NOT NULL,
  step_size decimal(15,6) NOT NULL,
  step_count int(10) unsigned NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (config_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE time_zones (
  time_zone_id smallint(5) unsigned NOT NULL DEFAULT '0',
  name varchar(255) NOT NULL DEFAULT '',
  used_order smallint(5) unsigned NOT NULL DEFAULT '0',
  user_tz tinyint(1) NOT NULL DEFAULT '0',
  country_id int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (time_zone_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE counter_quota (
  counter_id bigint(10) unsigned NOT NULL,
  multiplier double unsigned NOT NULL DEFAULT '2',
  PRIMARY KEY (counter_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE service_quota (
  service_id bigint(10) NOT NULL,
  multiplier double unsigned NOT NULL DEFAULT '2',
  PRIMARY KEY (service_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE tvm_service_to_uid_by_env (
  service_id int(11) unsigned NOT NULL,
  uid bigint(20) unsigned NOT NULL,
  comment varchar(255) DEFAULT NULL,
  environment enum('production','testing') NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (service_id,environment)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE tvm_services_by_env (
  service_id int(11) unsigned NOT NULL,
  name varchar(255) NOT NULL,
  comment varchar(255) DEFAULT NULL,
  environment enum('production','testing') NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (service_id,environment)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE tvm_services_by_function_by_env (
  `function` varchar(50) NOT NULL,
  service_id int(11) unsigned NOT NULL,
  comment varchar(255) DEFAULT NULL,
  environment enum('production','testing') NOT NULL,
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`function`,service_id,environment)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE ip_quota (
  ip varchar(150) NOT NULL,
  multiplier double unsigned NOT NULL DEFAULT '2',
  PRIMARY KEY (ip)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE user_quota (
  uid bigint(20) NOT NULL DEFAULT '0',
  multiplier double unsigned NOT NULL DEFAULT '2',
  PRIMARY KEY (uid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE internal_networks (
  `address` varchar(255) NOT NULL,
  PRIMARY KEY (`address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE guest_networks (
  `address` varchar(255) NOT NULL,
  PRIMARY KEY (`address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE gdpr_deleted_applications (
  application_id int NOT NULL,
  action_uid bigint NOT NULL,
  purge_time datetime NOT NULL,
  purged tinyint(1) NOT NULL,
  create_time datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (application_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE gdpr_deleted_partners (
  partner_id int NOT NULL,
  action_uid bigint NOT NULL,
  purge_time datetime NOT NULL,
  purged tinyint(1) NOT NULL,
  create_time datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (partner_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE gdpr_deleted_labels
(
  label_id    int      NOT NULL,
  action_uid  bigint   NOT NULL,
  purge_time  datetime NOT NULL,
  purged      tinyint(1) NOT NULL,
  create_time datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (label_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE organizations
(
    id                bigint(20) unsigned NOT NULL AUTO_INCREMENT,
    name              varchar(255) NOT NULL,
    billing_client_id bigint(20),
    owner_uid         bigint(20) NOT NULL,
    create_time       timestamp    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time       timestamp    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY (owner_uid),
    UNIQUE KEY (billing_client_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE organization_applications
(
  id              bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  organization_id bigint(20) NOT NULL,
  application_id  bigint(20) NOT NULL,
  create_time     timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time     timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY (application_id),
  KEY (organization_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
