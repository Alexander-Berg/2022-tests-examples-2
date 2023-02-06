use mobile;

INSERT IGNORE INTO tvm_services_by_env (service_id, name, environment) VALUES (1000502, 'direct_frontend', 'testing');
INSERT IGNORE INTO tvm_services_by_env (service_id, name, environment) VALUES (1000503, 'idm', 'testing');
INSERT IGNORE INTO tvm_services_by_env (service_id, name, environment) VALUES (1000504, 'takeout', 'testing');
INSERT IGNORE INTO tvm_services_by_env (service_id, name, environment) VALUES (1000505, 'passport_frontend', 'testing');

INSERT IGNORE INTO time_zones (time_zone_id, name, used_order, user_tz, country_id) VALUES (1, 'Europe/Moscow', 40, 1, 225);

INSERT IGNORE INTO layers_config (layer_id, weight) VALUES (1, 1);

INSERT IGNORE INTO application_categories VALUES (85,'Auto & Vehicles','Автомобили и транспорт','common');
INSERT IGNORE INTO application_categories VALUES (88,'Business','Бизнес','common');
INSERT IGNORE INTO application_categories VALUES (91,'Food & Drink','Еда и напитки','common');
INSERT IGNORE INTO application_categories VALUES (94,'House & Home','Жилье и дом','common');
INSERT IGNORE INTO application_categories VALUES (97,'Health & Fitness','Здоровье и фитнес','common');

INSERT IGNORE INTO special_partner_types VALUES
(0,      'organic'),
(5,      'facebook'),
(43,     'direct'),
(50,     'direct_auto'),
(136,    'mytarget'),
(30101,  'adwords'),
(69378,  'search_ads'),
(69648,  'doubleclick'),
(85825,  'tiktok'),
(122101, 'huawei_ads');

INSERT IGNORE INTO tracking_url_macros (partner_id, url_param, macro, status, platform) VALUES
(43,'click_id','{LOGID}','active',NULL),
(43,'click_id_deleted','{LOGID}','deleted',NULL),
(43,'google_aid','{GOOGLEAID}','active','android'),
(43,'ios_ifa','{IOSIFA}','active','iOS');

INSERT IGNORE INTO postback_templates VALUES
(3127,NULL,43,'http://yabs.yandex.ru/postback?package-name={app_package_name}&click-time={click_datetime}&reqid={click_id}&ip={click_ipv6}&ua={click_user_agent}&engagement-time={conversion_datetime}&device-model={device_model}&device-type={device_type}&gps-adid={google_aid}&installed-at={install_datetime}&idfa={ios_ifa}&match-type={match_type}&os={os_name}&os-version={os_version}&win-adid={windows_aid}&tracker=appmetrica&transaction-id={transaction_id}&tracker_device_id={appmetrica_device_id}&event-link-type=install','GET','','','cpi','Install Postback',0,NULL,'2018-07-20 08:22:14','2018-07-20 08:22:14','active','');
