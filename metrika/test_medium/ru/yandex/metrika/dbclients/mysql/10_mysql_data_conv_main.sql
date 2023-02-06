use conv_main;

insert ignore into tvm_services_by_env (service_id, name, environment) values (239, 'blackbox', 'testing');
insert ignore into tvm_services_by_env (service_id, name, environment) values (2000286, 'webmaster', 'testing');
insert ignore into tvm_services_by_env (service_id, name, environment) values (2000079, 'passport_intapi', 'testing');

insert ignore into time_zones (time_zone_id, name, used_order, user_tz, country_id) VALUES (1, 'Europe/Moscow', 40, 1, 225);

insert ignore into LayersConfig (LayerID, Weight) values (1, 1);
insert ignore into NanoLayersConfig (LayerID, Weight) values (1, 1);

insert ignore into currency (id, code, name, `order`) VALUES (643, 'RUB', 'Российский рубль', 0);

insert ignore into Messengers (Name, StrId, is_goal_messenger, is_traffic_source_messenger)
    VALUES ('Другой мессенджер: определено по меткам', 'unknown', 0, 1),
    ('Telegram', 'telegram', 1, 1),
    ('WhatsApp', 'whatsapp', 1, 1),
    ('Viber', 'viber', 1, 1),
    ('Skype', 'skype', 1, 1),
    ('WeChat', 'wechat', 0, 1),
    ('Яндекс.Мессенджер', 'yandex_chats', 1, 1),
    ('Facebook', 'facebook', 1, 0),
    ('ВКонтакте', 'vk', 1, 0);

insert ignore into SocialNetworks (Name, StrId, IsEnableForGoals, IsTrafficSourceSocialNetwork)
    VALUES ('ВКонтакте', 'vkontakte', 1, 1),
    ('Twitter', 'twitter', 1, 1),
    ('Facebook', 'facebook', 1, 1);
