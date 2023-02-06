CREATE TABLE modx_web_users (
    id int(10) NOT NULL AUTO_INCREMENT,
    username varchar(100) default '',
    -- skip other fields which useless right now
    unique (username),
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE modx_web_groups (
    id int(10) NOT NULL AUTO_INCREMENT,
    webgroup int(10) NOT NULL DEFAULT '0',
    webuser int(10) NOT NULL DEFAULT '0',
    PRIMARY KEY (id),
    UNIQUE KEY ix_group_user (webgroup,webuser),
    KEY webgroup (webgroup),
    KEY webuser (webuser)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE modx_event_log (
    id int(11) NOT NULL,
    eventid int(11) NULL DEFAULT '0',
    createdon int(11) NOT NULL DEFAULT '0',
    type tinyint(4) NOT NULL DEFAULT '1' COMMENT '1- information, 2 - warning, 3- error',
    source varchar(50) NOT NULL,
    description text NULL,
    PRIMARY KEY (id)
);


CREATE TABLE modx_s_admin_to_admin_point (
    id int(11) NOT NULL AUTO_INCREMENT,
    user_id int(11) NOT NULL,
    to_user_id int(11) NOT NULL,
    PRIMARY KEY (id),
    KEY user_id (user_id),
    KEY to_user_id (to_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE modx_web_user_attributes (
    id int(10) NOT NULL AUTO_INCREMENT,
    internalKey int(10) NOT NULL DEFAULT '0',
    fullname varchar(100) NOT NULL DEFAULT '',
    name_small varchar(100),
    photo varchar(255) NOT NULL DEFAULT '' COMMENT 'link to photo',
    address varchar(255) NOT NULL DEFAULT '', -- there is no default in production, but no one row with null too
    blocked int(1) NOT NULL DEFAULT '0',
    interface enum('restaurant','hotel') NOT NULL DEFAULT 'restaurant',
    saving_up_for varchar(50) DEFAULT '',
    phone varchar(100) NOT NULL DEFAULT '',
    email varchar(100) NOT NULL DEFAULT '',
    date_reg int NOT NULL,
    best2pay_card_token varchar(50) NOT NULL DEFAULT '',
    best2pay_card_exp varchar(50) NOT NULL DEFAULT '',
    best2pay_card_pan varchar(50) NOT NULL DEFAULT '',
    best2pay varchar(19) NOT NULL DEFAULT '' COMMENT 'если создан виртуальный счет МИБ best2pay', -- there is no default in production
    best2pay_phone int(1) NOT NULL DEFAULT '0' COMMENT '1 - привязкан телефон к аккаунту B2P',
    b2p_block_mcc int(1) DEFAULT '0' COMMENT 'Сработала или проставлена блокировка МСС кодов',
    b2p_block_full int(1) NOT NULL DEFAULT '0' COMMENT 'полная блокировка по trancode',
    is_admin_reg int(1) NOT NULL,
    date_first_pay int(11) NOT NULL,
    is_free_procent int(1) NOT NULL DEFAULT '0' COMMENT '1 - не брать комиссию 5%',
    trans_guest int(1) DEFAULT '0' COMMENT 'Переносить транзакционные издержки на гостя - галоча',
    trans_guest_block int(1) DEFAULT '1' COMMENT 'Переносить транзакционные издержки на гостя - выводить сам блок',
    role int(10) NOT NULL DEFAULT '1',
    is_blocked int(1) NOT NULL DEFAULT '0',
    address_ur varchar(100) NOT NULL DEFAULT '',
    inn varchar(100) NOT NULL DEFAULT '',
    bank_name varchar(100) NOT NULL DEFAULT '',
    bank_inn varchar(100) NOT NULL DEFAULT '',
    kpp varchar(100) NOT NULL DEFAULT '',
    bik varchar(100) NOT NULL DEFAULT '',
    rs varchar(100) NOT NULL DEFAULT '',
    card_number varchar(100) NOT NULL DEFAULT '',
    kor_schet varchar(100) NOT NULL DEFAULT '',
    floor int NOT NULL DEFAULT '1',
    room int NOT NULL DEFAULT '1',
    azs int NOT NULL DEFAULT '0',
    maid_id int NOT NULL DEFAULT '1',
    show_name int(1) NOT NULL DEFAULT '1',
    send_report int(1) NOT NULL DEFAULT '0',
    send_report_time int(1) NOT NULL DEFAULT '0',
    agent_procent numeric NOT NULL DEFAULT '0',
    promocode varchar(100) NOT NULL DEFAULT '',
    confirmation_code varchar(100) NOT NULL DEFAULT '',
    promo_code varchar(100) NOT NULL DEFAULT '',
    pay_method varchar(100) NOT NULL DEFAULT '',
    review_send_to varchar(100) NOT NULL DEFAULT '',
    parent_id int NOT NULL DEFAULT '0',
    change_code varchar(100) NOT NULL DEFAULT '',
    change_code_md5 varchar(100) NOT NULL DEFAULT '',
    change_password_time int NOT NULL DEFAULT '0',
    osmi_link varchar(100) NOT NULL DEFAULT '',
    is_new_interface int(1) NOT NULL DEFAULT '0',

    PRIMARY KEY (id),
    KEY userid (internalKey)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Contains information about the backend users.';


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


CREATE TABLE modx_web_users_orgs (
    id int(10) NOT NULL AUTO_INCREMENT,
    user_id int(10) NOT NULL DEFAULT '0',
    to_user_id int(10) NOT NULL DEFAULT '0',
    status int(1) NOT NULL DEFAULT '0',
    show_in_menu int(1),
    code varchar(25) NOT NULL DEFAULT '',
    date_reg int NOT NULL,
    date_send int NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
