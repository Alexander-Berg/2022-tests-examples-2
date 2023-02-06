-- RBAC

drop schema if exists rbac;

create schema rbac collate utf8_general_ci;

use rbac;

create table appmetrica_grants_internal
(
	staff_login varchar(256) not null,
	uid bigint unsigned not null,
	application_id int unsigned not null,
	grant_type enum('view', 'edit') not null,
	constraint manager
		unique (uid, application_id, grant_type)
);

create table appmetrica_managers
(
	staff_login varchar(256) not null,
	uid bigint unsigned not null,
	role_id tinyint(3) not null,
	comment varchar(256) null,
	constraint manager
		unique (uid, role_id)
);

create table class
(
	class bigint unsigned auto_increment
		primary key
);

ALTER TABLE class AUTO_INCREMENT=1001;

create table comments
(
	uid bigint unsigned not null,
	obj_type tinyint unsigned not null,
	obj_id bigint unsigned not null,
	comment varchar(255) not null,
	primary key (uid, obj_type, obj_id)
);

create index obj_id
	on comments (obj_id);

create table grants_internal
(
	staff_login varchar(256) not null,
	uid bigint unsigned not null,
	counter_id int unsigned not null,
	grant_type enum('view', 'edit') not null,
	constraint manager
		unique (uid, counter_id, grant_type)
);

create table grants_internal_tmp
(
	staff_login varchar(256) not null,
	uid bigint unsigned not null,
	counter_id int unsigned not null,
	grant_type enum('view', 'edit') not null,
	constraint manager
		unique (uid, counter_id, grant_type)
);

create table grants_log
(
	id bigint unsigned auto_increment
		primary key,
	action_uid bigint unsigned not null,
	grantee bigint unsigned not null,
	obj_type tinyint unsigned not null,
	obj_id bigint unsigned not null,
	action enum('add', 'update', 'delete') not null,
	time datetime default CURRENT_TIMESTAMP not null
);

create index grantee
	on grants_log (grantee);

create index obj_id
	on grants_log (obj_id);

create table managers
(
	staff_login varchar(256) not null,
	uid bigint unsigned not null,
	role_id tinyint(3) not null,
	comment varchar(256) null,
	constraint manager
		unique (uid, role_id)
);

create table obj_types
(
	obj_type tinyint unsigned auto_increment
		primary key,
	descr varchar(255) default '' not null
);

create table objects
(
	class bigint unsigned default 0 not null,
	obj_type tinyint unsigned default 0 not null,
	obj_id bigint unsigned default 0 not null,
	serial smallint default 0 not null,
	created_at datetime null,
	constraint NewIndex
		unique (class, obj_type, obj_id),
	constraint reverse_primary
		unique (obj_id, obj_type, class)
);

create index class_obj_id_type_idx
	on objects (class, obj_id, obj_type);

create table permissions
(
	perm_id int unsigned auto_increment
		primary key,
	name varchar(255) default '' not null
);

create table proxy_tokens
(
	token char(36) collate ascii_bin default '' not null
		primary key,
	domain varchar(255) collate ascii_bin null,
	uid bigint null,
	usage_count int default 0 null,
	last_modified timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	created timestamp default CURRENT_TIMESTAMP not null,
	constraint uid
		unique (uid, domain)
);

create table role_perm
(
	role_id tinyint unsigned default 0 not null,
	obj_type tinyint(3) default 0 not null,
	perm_id int unsigned default 0 not null,
	constraint NewIndex
		unique (role_id, obj_type, perm_id)
);

create table roles
(
	role_id tinyint(3) auto_increment
		primary key,
	name varchar(255) default '' not null,
	descr varchar(255) default '' not null,
	help varchar(255) default '' null comment 'for IDM'
);

create table service_roles
(
	name varchar(255) default '' not null,
	descripion varchar(1000) default '' not null,
	class tinyint(3) not null,
	primary key (name, class)
);

create table uid_comments
(
	uid bigint default 0 not null,
	uid_for bigint default 0 not null,
	comment varchar(255) not null,
	primary key (uid, uid_for)
);

create table uid_role_class (
    uid bigint(20) unsigned not null default '0',
    role_id tinyint(3) unsigned not null default '0',
    class bigint(20) unsigned not null default '0',
    serial smallint(6) not null default '0',
    descr varchar(255) not null default '',
    create_time datetime default null,
    internal tinyint(1) default '0',
    unique key NewIndex (uid, role_id, class),
    key class (class)
);

create table uid_service_roles
(
	uid bigint not null,
	login varchar(255) not null,
	class tinyint(3) not null,
	primary key (uid, login, class)
);

create table users
(
	uid bigint unsigned default 0 not null
		primary key,
	login varchar(128) null,
	create_time datetime not null,
	per_page int null,
	table_mode text null,
	filter varchar(20) null,
	chart_type text null,
	`group` varchar(20) null,
	sort varchar(20) null,
	yandexuid text null,
	flash_enabled tinyint(1) default 1 null,
	flash_animation tinyint(1) default 1 null,
	progressbar_enabled tinyint(1) default 1 null,
	selected_country varchar(20) null,
	counters_get_more int default 0 null,
	counters_per_group int default 0 null,
	gui mediumtext null,
	max_tree_childs int default 0 null,
	closed_counter_groups varchar(50) not null,
	group_chart text null,
	mp2_offer tinyint default 0 null,
	mp2_migration tinyint(1) null,
	mp2_last_mail date null,
	subscription_emails_unchecked tinyint default 0 null,
	subscription_emails tinyint default 0 null
);

