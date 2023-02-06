CREATE TABLE modx_web_user_attributes (
  id int NOT NULL,
  date_reg int(11) NOT NULL DEFAULT '0',
  internalKey int NOT NULL DEFAULT '0',
  name_small varchar(100) NOT NULL,
  fullname varchar(100) NOT NULL DEFAULT '',
  blocked int NOT NULL DEFAULT '0',
  photo varchar(255) NOT NULL DEFAULT '',
  phone varchar(100) NOT NULL DEFAULT '',
  interface varchar(255) NOT NULL DEFAULT '',
  show_name int not null default '0',
  saving_up_for varchar(255) default '',
  trans_guest_block int not null default '0',
  trans_guest int not null default '0',
  pay_page_bw int not null default '0',
  pay_page_option int not null default '0',
  b2p_block_mcc int default '0',
  proc1 int not null default '5',
  proc2 int not null default '7',
  proc3 int not null default '10',
  proc4 int not null default '15',
  proc_all int,
  is_admin_reg int(1) NOT NULL DEFAULT 0,
  price1 int(2) DEFAULT '50' COMMENT 'Фиксированная сумма чаевых для отображения на странице оплаты 1',
  price2 int(2) DEFAULT '100' COMMENT 'Фиксированная сумма чаевых для отображения на странице оплаты 2',
  price3 int(2) DEFAULT '300' COMMENT 'Фиксированная сумма чаевых для отображения на странице оплаты 3',
  price4 int(2) DEFAULT '500' COMMENT 'Фиксированная сумма чаевых для отображения на странице оплаты 4',
  price_all int(2) DEFAULT '0' COMMENT 'Сумма по умолчанию при открытии страницы оплаты'
);

CREATE TABLE modx_web_users_org (
  id int NOT NULL,
  user_id int NOT NULL,
  to_user_id int NOT NULL,
  status int NOT NULL,
  show_in_menu int not null default 1
);

CREATE TABLE modx_web_groups (
  webuser int not null,
  webgroup int not null
);

CREATE TABLE `modx_s_admin_to_admin_point` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `to_user_id` int NOT NULL,
  `who` int NOT NULL,
  `date_time` int NOT NULL
);

CREATE TABLE modx_web_users_pays (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `to_user_id` int(11) NOT NULL,
  `to_user_sub_id` int(11) NOT NULL DEFAULT '0',
  `card_id` int(11) NOT NULL DEFAULT '0',
  `transaction_id` varchar(50) DEFAULT NULL,
  `transaction_status` varchar(50) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `amount_trans` decimal(10,2) DEFAULT '0.00',
  `date_created` int(11) NOT NULL,
  `transaction_status_date` int(11) NOT NULL DEFAULT '0',
  `transaction_pay_date` int(11) NOT NULL,
  `language` varchar(3) NOT NULL,
  `test` int(1) NOT NULL,
  `is_blago` int(1) NOT NULL,
  `procent` int(1) NOT NULL COMMENT '1 - процент с приглашенного друга или 2 - процент ЯК или 3 - проценит Агенту или 4 - процент сайта или 5 - заявка на вывод; 6 - Компенсация комиссии от системы по акции; 7 - Компенсация от Сервиса; 8 - оплата платной СМС;',
  `who` int(11) NOT NULL,
  `type` int(1) NOT NULL COMMENT '0 - приход, 1 - вывод',
  `is_apple` int(1) NOT NULL,
  `is_google` int(1) NOT NULL,
  `is_samsung` int(1) NOT NULL,
  `is_ecommpay` int(1) NOT NULL,
  `is_best2pay` int(1) NOT NULL,
  `best2pay_fee` decimal(10,2) NOT NULL,
  `is_mp` int(1) NOT NULL DEFAULT '0',
  `code` int(1) NOT NULL,
  `room_id` int(11) NOT NULL,
  `comment` varchar(255) NOT NULL,
  `parent_id` int(11) NOT NULL,
  `idempotenceKey` varchar(50) NOT NULL,
  `message` varchar(255) NOT NULL,
  `email` varchar(50) NOT NULL,
  `pan` varchar(20) DEFAULT NULL,
  `is_b2p_fail` int(1) NOT NULL DEFAULT '0',
  `is_yandex` int(11) NOT NULL DEFAULT '0' COMMENT 'Yandex Pay',
  PRIMARY KEY (`id`),
  UNIQUE KEY `transaction_id` (`transaction_id`)
);

CREATE TABLE modx_event_log (
    `id` int(11) NOT NULL,
    `eventid` int(11) NULL DEFAULT '0',
    `createdon` int(11) NOT NULL DEFAULT '0',
    `type` tinyint(4) NOT NULL DEFAULT '1' COMMENT '1- information, 2 - warning, 3- error',
    `user` int(11) NOT NULL DEFAULT '0',
    `usertype` tinyint(4) NOT NULL DEFAULT '0',
    `source` varchar(50) NOT NULL,
    `description` text NULL,
    PRIMARY KEY (`id`)
);

CREATE TABLE `modx_system_settings` (
  `setting_name` varchar(50) NOT NULL DEFAULT '',
  `setting_value` text,
  PRIMARY KEY (`setting_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Contains Content Manager settings.';

CREATE TABLE `sbp_banks` (
  `id` varchar(20) NOT NULL,
  `title` varchar(255) NOT NULL,
  `latin_title` varchar(255) NOT NULL,
  `in_short_list` int(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `Short_list_banks` (`in_short_list`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Contains SBP banks';


CREATE TABLE `modx_web_users_reviews` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `user_id` int(11) NOT NULL,
    `user_sub_id` int(11) NOT NULL,
    `star` int(1) NOT NULL,
    `review` varchar(512) NOT NULL,
    `photo` varchar(255) NOT NULL,
    `is_send_phone` int(1) NOT NULL COMMENT 'если отправили отзыв руковолителю',
    `service` int(1) DEFAULT '0',
    `quality` int(1) DEFAULT '0',
    `clean` int(1) DEFAULT '0',
    `atmosphere` int(1) DEFAULT '0',
    `speed` int(1) DEFAULT '0',
    `good_atmosphere` int(1) DEFAULT '0',
    `delicious_food` int(1) DEFAULT '0',
    `delightful_service` int(1) DEFAULT '0',
    `good_speed` int(1) DEFAULT '0',
    `master_gold_hand` int(1) DEFAULT '0' COMMENT 'Мастер золотые руки (Салон красоты)',
    `pay_page_type` int(1) DEFAULT '0' COMMENT 'Тип платежной страницы',
    `date_time` int(11) NOT NULL,
    `order_id` int(11),
    PRIMARY KEY (`id`),
    UNIQUE KEY `order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE refund_plus (
	transaction_id int(11) NOT NULL ,
	cashback_refunded INT(1) DEFAULT 0 NOT NULL,
	unique KEY `transaction_id` (`transaction_id`),
	KEY `cashback_refunded` (`cashback_refunded`)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci
COMMENT='Contains transactions to refund plus';

CREATE TABLE `modx_blacklist_cards` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `number` varchar(16) NOT NULL,
  `comment` varchar(255) NOT NULL,
  `date_time` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  FULLTEXT KEY `number` (`number`)
) ENGINE=InnoDB AUTO_INCREMENT=138 DEFAULT CHARSET=utf8;

CREATE TABLE `modx_users_whitelist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT '0' COMMENT 'админ места или получатель',
  `date_time` int(11) DEFAULT '0' COMMENT 'время добавления',
  `active` int(1) DEFAULT '1' COMMENT '1 - в белом листе',
  `vip` int(1) DEFAULT '0' COMMENT '1 - VIP клиент',
  PRIMARY KEY (`id`),
  KEY `modx_users_whitelist_vip_index` (`vip`),
  KEY `modx_users_whitelist_active_index` (`active`),
  KEY `modx_users_whitelist_user_id_index` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='белый список пользователей';
