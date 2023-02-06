-- CONV_MAIN

drop schema if exists conv_main;

create schema conv_main collate utf8_general_ci;

use conv_main;

SET NAMES 'utf8';

create table code_options
(
    counter_id bigint unsigned not null
        primary key,
    alternative_cdn tinyint(3) default 0 not null,
    async tinyint(3) default 1 not null,
    ecommerce tinyint(3) default 0 not null,
    ecommerce_object varchar(256) null,
    in_one_line tinyint(3) default 0 not null,
    track_hash tinyint(3) default 0 not null,
    wv_enabled tinyint(3) default 0 not null,
    wv_version int default 2 not null,
    xml_site tinyint(3) default 0 not null,
    maps tinyint(3) default 0 not null,
    nda tinyint(3) default 0 not null,
    telephony tinyint(3) default 0 not null,
    publisher_enabled tinyint(3) default 0 not null,
    publisher_schema enum('microdata', 'json_ld', 'ontheio', 'schema', 'opengraph', 'linkpulse', 'mediator') null,
    clickmap tinyint(3) default 0 not null,
    webvisor_load_player enum('proxy', 'on-your-behalf') default 'proxy' not null,
    update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    incognito  enum ('disabled', 'enabled_by_classifier', 'disabled_by_user', 'enabled_by_user') not null,
    collect_first_party_data tinyint(1) default 1 not null,
    statistics_over_site tinyint(1) default 1 not null
);

create table informer
(
    counter_id bigint unsigned not null
        primary key,
    enabled tinyint(3) default 0 not null,
    color_arrow tinyint(3) default 1 not null,
    color_text tinyint(3) default 0 not null,
    color_start int unsigned not null,
    color_end int unsigned not null,
    indicator enum('pageviews', 'visits', 'uniques') default 'pageviews' not null,
    size tinyint(3) default 3 not null,
    type enum('simple', 'ext') default 'ext' not null
);

create table AdvEngines2
(
	Id smallint auto_increment
		primary key,
	AdvEngine varchar(1000) not null,
	ServiceNamePattern varchar(1000) not null,
	RefererPattern varchar(1000) not null,
	StrId varchar(255) not null,
	Domain varchar(1000) null
);

create table AdvEnginesPlaces
(
	EngineID int(1) unsigned not null,
	PlaceID int(2) unsigned not null,
	StrID varchar(1000) not null,
	primary key (EngineID, PlaceID)
);

create table AdvEnginesPlacesNames
(
	Id bigint unsigned not null
		primary key,
	StrID varchar(1000) not null,
	Text varchar(1000) not null
);

create table AdvPlaces
(
	Id smallint default 0 not null
		primary key,
	AdvEngineID smallint default 0 not null,
	AdvPlaceID smallint default 0 not null,
	PlaceName text null,
	StrId varchar(255) not null,
	constraint `UNIQUE`
		unique (AdvEngineID, AdvPlaceID)
);

create table BadUniqIDs
(
	UniqID bigint unsigned not null
);

create table BrowserEngines
(
	Id int unsigned auto_increment
		primary key,
	Name varchar(100) not null,
	constraint Name
		unique (Name)
);

create table CookieRestrictedSubdomains
(
	Id int auto_increment
		primary key,
	DomainSuffix text not null,
	CookieLifeTime int not null
);

create table Filters
(
	ID int auto_increment
		primary key,
	CounterID int not null,
	Serial smallint not null,
	AttributeName enum('Title', 'ClientIP', 'URL', 'Referer', 'UniqID') not null,
	Type enum('equal', 'start', 'contain', 'not_equal', 'not_start', 'regexp', 'not_regexp', 'not_contain', 'interval', 'not_in_interval', 'cut_parameter', 'cut_fragment', 'not_me', 'only_mirrors', 'merge_https_and_http', 'cut_all_parameters', 'to_lower', 'replace_domain') not null,
	Value text not null,
	Data text not null,
	UpdateTime timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	Status enum('Active', 'Deleted', 'Disabled') default 'Active' not null,
	Name text not null,
	WithSubdomains tinyint(1) default 0 not null
);

create index IX_CounterID
	on Filters (CounterID);

create index IX_UpdateTime
	on Filters (UpdateTime);

create table GlobalFilters
(
	ID int auto_increment
		primary key,
	Type enum('IPInterval', 'RefererPattern', 'URLPattern', 'FirstSignificantSubdomainReferer', 'FirstSignificantSubdomainURL') not null,
	Status enum('Active', 'Deleted', 'Disabled') not null,
	Data text not null,
	UpdateTime timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	Name text not null
);

create index UpdateTime
	on GlobalFilters (UpdateTime);

create table GlobalMetrageDB
(
	ID int unsigned auto_increment
		primary key,
	Priority tinyint unsigned not null,
	URL text not null
);

create table IPNetworks
(
	ID int(11) unsigned auto_increment
		primary key,
	ParentID int(11) unsigned not null,
	DescriptionID int(11) unsigned not null,
	IPFirst int(11) unsigned not null,
	IPLast int(11) unsigned not null,
	constraint `Unique`
		unique (IPFirst, IPLast, ParentID, DescriptionID)
);

create table IPNetworksDescriptions
(
	ID int(11) unsigned auto_increment
		primary key,
	Description varchar(255) not null,
	constraint `Unique`
		unique (Description)
);

create table IPToLeafNetwork
(
	IPFirst int unsigned default 0 not null
		primary key,
	NetworkID int unsigned null
);

create table Interests
(
	Id int not null
		primary key,
	Interest varchar(50) null,
	StrId varchar(255) not null
);

create table LayersConfig
(
	LayerID int(3) unsigned default 0 not null
		primary key,
	Weight int(3) unsigned default 0 not null
);

create table Messengers
(
	Id smallint auto_increment
		primary key,
	Name varchar(1000) not null,
	StrId varchar(255) not null,
	is_goal_messenger tinyint(1) not null default 0,
	is_traffic_source_messenger tinyint(1) not null default 0
);

create table MobilePhones
(
	Id bigint(10) unsigned auto_increment
		primary key,
	Weight smallint(5) default 0 not null,
	MobilePhone varchar(1000) not null,
	Pattern varchar(1000) not null,
	IsTablet tinyint(1) unsigned default 0 not null,
	OS smallint unsigned default 0 not null,
	AlternativeNames varchar(1000) default '' not null,
	StrId varchar(255) not null,
	constraint MobilePhone
		unique (MobilePhone)
);

create table NanoLayersConfig
(
	LayerID int(3) unsigned default 0 not null
		primary key,
	Weight int(3) unsigned default 0 not null
);

create table OLAPExampleReports_REMOVE
(
	ID int unsigned auto_increment
		primary key,
	Query mediumtext not null,
	Title mediumtext not null
);

create table OLAPFavoriteReports_REMOVE
(
	ID int unsigned auto_increment
		primary key,
	CounterID int unsigned not null,
	Query mediumtext not null,
	Title mediumtext not null,
	CreateTime datetime not null,
	UpdateTime timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	Deleted tinyint default 0 not null
);

create index IX1
	on OLAPFavoriteReports_REMOVE (CounterID);

create table OLAPLastReports_REMOVE
(
	ID int unsigned auto_increment
		primary key,
	CounterID int unsigned not null,
	Query mediumtext not null,
	QueryHash varchar(32) not null,
	Title mediumtext not null,
	CreateTime datetime not null,
	UpdateTime timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	constraint UK1
		unique (CounterID, QueryHash)
);

create table OS
(
	Id bigint(10) unsigned default 0 not null
		primary key,
	Pattern varchar(1000) not null,
	IsMobile tinyint(1) not null,
	Weight int default 0 not null,
	IsNotMobile tinyint(1) default 0 not null
);

create table OS2
(
	Id bigint(10) unsigned default 0 not null
		primary key,
	Parent_Id bigint(10) unsigned null,
	OS varchar(1000) not null,
	UATraitsName varchar(1000) not null,
	OSMajor varchar(3) default '' not null,
	OSMinor varchar(3) default '' not null,
	IsMobile tinyint(1) default 0 not null,
	IsNotMobile tinyint(1) default 0 not null,
	IsOther tinyint(1) unsigned default 0 not null,
	Sort int default 100 not null,
	StrId varchar(255) not null
);

create table OS2Dict
(
	Id bigint default 0 not null,
	OS varchar(1000) not null,
	Parent_Id bigint(10) unsigned null,
	RootId bigint unsigned null
);

create table OSTree
(
	Id int not null
		primary key,
	Parent_Id int unsigned null,
	OS varchar(1000) not null,
	IsOther tinyint(1) unsigned default 0 not null,
	Sort int not null
);

create table PageFormats
(
	Id smallint auto_increment
		primary key,
	Name varchar(1000) not null,
	StrId varchar(255) not null
);

create table Place
(
	PlaceID int auto_increment
		primary key,
	PlaceParentID int default 0 not null,
	PlaceSequentID int default 0 not null,
	ExtBlockID int default 0 not null,
	BannerLimit int default 0 not null,
	BannerType tinyint default 0 not null,
	PlaceAll tinyint default 0 not null,
	AddContexts tinyint default 1 not null,
	PlaceSelect tinyint default 0 not null,
	Flags set('OrderUnique', 'PlaceWrap') charset koi8r default '' null,
	WantStat tinyint default 0 not null,
	Options set('wantstat', 'mobile', 'deleted', 'detailed-geo') default '' not null,
	PlaceDescription varchar(255) null
);

create table QRCodeProviders
(
	Id smallint auto_increment
		primary key,
	Name varchar(1000) not null,
	StrId varchar(255) not null
);


create table RecommendationSystems
(
    Id smallint auto_increment
        primary key,
    Name varchar(1000) not null,
    StrId varchar(255) not null
);

create table RobotFilters
(
	Id bigint(10) unsigned default 0 not null
		primary key,
	Weight smallint(5) default 0 not null,
	RobotName varchar(1000) not null,
	Pattern varchar(1000) not null,
	URLAppEnginePattern varchar(1000) not null,
	Tokens varchar(255) not null,
	Type enum('UserAgent', 'IPInterval') not null,
	IPRange varchar(255) not null
);

create table RobotUserAgent
(
	Id bigint(10) unsigned default 0 not null
		primary key,
	Weight smallint(5) default 0 not null,
	RobotName varchar(1000) not null,
	Pattern varchar(1000) not null,
	URLAppEnginePattern varchar(1000) not null,
	Tokens varchar(255) not null
);

create table SearchEngines
(
	Id bigint(10) unsigned auto_increment
		primary key,
	SearchEngine varchar(1000) not null,
	ParentId bigint(10) unsigned null,
	weight int(8) not null,
	URL varchar(1000) not null,
	form_num int null,
	field_name varchar(1000) not null,
	Hide tinyint(1) unsigned default 0 not null,
	CheckType enum('Full', 'Redirect', 'None') default 'Full' not null,
	PageParameterPattern varchar(255) null,
	PageParameterOffset tinyint(1) null,
	PageParameterDivisor tinyint(1) null,
	StrId varchar(255) not null,
	Domain varchar(1000) null
);

create index FK_ParentId
	on SearchEngines (ParentId);

create table SearchEnginesDict
(
	Id bigint(10) unsigned default 0 not null,
	SearchEngine varchar(1000) not null,
	ParentId bigint(10) unsigned null,
	RootId bigint unsigned null
);

create table SearchEngines_Patterns
(
	Id bigint(10) unsigned auto_increment comment 'In order of priority'
		primary key,
	SearchEngineId bigint(10) unsigned not null,
	Pattern varchar(1000) not null comment '1st subpattern is search phrase',
	QuickPattern varchar(1000) not null comment 'for check with strcasecmp',
	Charset enum('Auto', 'KOI8R') default 'Auto' not null
);

create index FK_SearchEngineId
	on SearchEngines_Patterns (SearchEngineId);

create table SearchEngines_SimplePatterns
(
	SearchEngineID int unsigned not null
		primary key,
	Domains varchar(1000) not null comment 'Without ''www'', comma separated.',
	Parameters varchar(1000) not null comment 'Comma separated.',
	PhraseRequired tinyint(1) default 1 not null,
	Charset enum('Auto', 'KOI8R', 'GB2312') default 'Auto' not null
);

create table ShareServicePattern
(
	Id bigint unsigned default 0 not null,
	ServiceName varchar(1000) default '' not null,
	DomainWithoutWWW varchar(1000) default '' not null,
	Pattern varchar(1000) default '' not null,
	URLPosition tinyint unsigned default 0 not null,
	TitlePosition tinyint unsigned default 0 not null,
	ServiceText varchar(1000) default '' not null
);

create table SocialNetworks
(
	Id smallint auto_increment
		primary key,
	Name varchar(1000) not null,
	FirstSignificantSubdomain varchar(1000) not null,
	Pattern varchar(1000) not null comment 'may contain subpattern with social network page',
	Exceptions varchar(1000) not null,
	StrId varchar(255) not null,
	Domain varchar(1000) null,
	IsEnableForGoals tinyint(1) not null default '0',
	IsTrafficSourceSocialNetwork tinyint(1) not null default '0',
	ExternalRegexp varchar(1000) not null default ''
);

create table StatDB
(
	Id int unsigned not null
		primary key,
	Host text not null,
	Port int not null,
	BaseName text not null
);

create table TraficSources
(
	Id bigint(10) auto_increment
		primary key,
	TraficSource varchar(1000) not null,
	StrId varchar(255) not null,
	UTMMediumPattern varchar(1000) not null
);

create table TraficSources2
(
	Id bigint(10) not null
		primary key,
	TraficSource varchar(1000) not null,
	StrId varchar(255) not null
);

create table TraficSources_Patterns
(
	TraficSourceID bigint(10) not null,
	EngineID smallint not null,
	Domains varchar(1000) default '' not null comment 'Without ''www'', comma separated.',
	FirstSignificantSubdomain varchar(1000) default '' not null,
	Parameters varchar(1000) default '' not null comment 'Comma separated.',
	CheckPattern varchar(1000) default '' not null,
	ExtractPattern varchar(1000) default '' not null,
	Exceptions varchar(1000) default '' not null,
	PhraseRequired tinyint(1) default 0 not null,
	Charset enum('Auto', 'KOI8R', 'GB2312') default 'Auto' not null,
	RejectPattern varchar(1000) default '' not null,
	SearchEngineIDForAdvEngine smallint default 0 not null,
	UTMSourcePattern varchar(1000) default '' not null comment 'All rules for current (TraficSourceID, EngineID) pair will be processed on any match of UTMSourcePattern, see METR-15980'
);

create table TraficSources_bak
(
	Id bigint(10) default 0 not null,
	TraficSource varchar(1000) not null,
	StrId varchar(255) not null,
	UTMMediumPattern varchar(1000) not null
);

create table TraficSources_new
(
	Id bigint(10) default 0 not null,
	TraficSource varchar(1000) not null,
	StrId varchar(255) not null,
	UTMMediumPattern varchar(1000) not null
);

create table UserAgent
(
	Id bigint(10) unsigned auto_increment
		primary key,
	Weight smallint(5) default 0 not null,
	Sort int default 0 not null,
	UserAgent varchar(1000) not null,
	Pattern varchar(1000) default '' not null,
	IsMobile tinyint(1) default 0 not null,
	Tokens varchar(255) default '' not null,
	UATraitsName varchar(1000) default '' not null,
	StrId varchar(255) not null,
	constraint UATraitsName
		unique (UATraitsName)
);

create table VacuumEvents
(
	StrId varchar(255) not null
		primary key,
	Name varchar(1000) not null
);

create table VacuumSurfaces
(
	StrId varchar(255) not null
		primary key,
	Name varchar(1000) not null
);

create table YandexDomainPatterns
(
	Id smallint auto_increment
		primary key,
	URLDomainPattern varchar(1000) default '' not null
);

create table YandexSearchEngines
(
	Id bigint(10) unsigned auto_increment comment 'In order of priority'
		primary key,
	SearchEngineId int(10) not null,
	Domains varchar(1000) not null,
	FromWithoutDomainPattern varchar(1000) not null
);

create table ad_goals
(
	goal_id int unsigned not null
		primary key,
	counter_id int unsigned default 0 not null,
	serial smallint default 0 not null,
	name varchar(255) null,
	depth int unsigned not null,
    goal_type enum ('url', 'number', 'step', 'action', 'offline', 'call', 'email', 'phone', 'form', 'cdp_order_in_progress', 'cdp_order_paid', 'messenger', 'file', 'search', 'button', 'social', 'e_cart', 'e_purchase', 'conditional_call', 'payment_system', 'a_cart', 'a_purchase', 'contact_data', 'login_with_yandexcid') not null,
    status enum('Active', 'Deleted', 'Archived', 'Hidden') default 'Active' not null,
    create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	mod_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	goal_flag enum('', 'order', 'basket') default '' not null,
	prev_goal_id int unsigned default 0 not null,
	parent_goal_id int default 0 not null,
	class tinyint default 1 null,
	last_step tinyint(1) unsigned default 0 not null,
	is_retargeting tinyint(1) unsigned default 0 not null,
	direct_retargeting tinyint(1) default 0 not null,
	display_retargeting tinyint(1) default 0 not null,
	adfox_retargeting tinyint(1) default 0 not null,
	banana_retargeting tinyint(1) default 0 not null,
	default_price decimal(15,6) NOT NULL DEFAULT 0.000000,
    source enum('user','auto') default 'user' not null,
    hide_phone_number tinyint(1) default null,
    is_favorite tinyint(1) default 0 not null,
    partner_goal_id int unsigned default 0 not null
);

create index i_ad_goals_counter_id
	on ad_goals (counter_id);

create index mod_time
	on ad_goals (mod_time);

create table ad_goals_urls
(
	goal_id int unsigned not null,
	serial int unsigned not null,
    `field` enum('call_first','call_missed','call_tag','call_duration') default null,
	pattern_type enum('exact','start','contain','regexp','action','form_id','form_name','form_xpath','messenger','all_files','file','search','btn_href','btn_path','btn_id','btn_content','btn_type','all_social','social','greater','less','between','regexp_action','contain_action') not null,
	url varchar(16384) not null,
	primary key (goal_id, serial)
);

create table applications_old
(
	id int(11) unsigned auto_increment
		primary key,
	uid bigint unsigned not null,
	status enum('active', 'deleted') default 'active' not null,
	name varchar(255) not null,
	time_zone_id int(11) unsigned default 1 not null,
	create_time datetime default CURRENT_TIMESTAMP null
);

create index uid
	on applications_old (uid);

create table big_counters
(
	counter_id int unsigned not null
		primary key,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP
);

create table big_counters_empty
(
	counter_id int unsigned not null
		primary key,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP
);

create table big_counters_tmp_mtnano_018_20191023
(
	counter_id int unsigned not null
		primary key,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP
);

create table boost_domain_override
(
	domain varchar(128) not null
		primary key,
	has_metrika tinyint(1) default 0 null
);

create table catalogues
(
	id int(11) unsigned not null
		primary key,
	rus_name varchar(100) not null,
	parents varchar(100) not null
);

create table chart_annotations
(
	id int unsigned auto_increment
		primary key,
	owner_id bigint unsigned not null,
	create_time timestamp default CURRENT_TIMESTAMP not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	deleted tinyint(1) default 0 not null,
	date date null,
	time time null,
	title varchar(255) null,
	message varchar(1023) null,
	counter_id int unsigned not null,
	`group` enum('A', 'B', 'C', 'D', 'E') null
);

create index counter_id
	on chart_annotations (counter_id);

create index date
	on chart_annotations (date);

create table chosen_tbl
(
	uid bigint unsigned not null,
	counter_id int unsigned not null,
	primary key (uid, counter_id)
);

create table conversion_batch_id_counter_request_queue
(
	item_id int unsigned auto_increment
		primary key,
	czxid bigint null,
	ctime bigint null,
	batch_id varchar(20) null,
	uploading_id int unsigned not null,
	uploading_type enum('YCLID', 'OFFLINE_CONVERSION') null,
	line_quantity int not null,
	create_time timestamp default CURRENT_TIMESTAMP not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	is_processed tinyint(1) default 0 null,
	constraint conversion_update_event_czxid_ctime_batch_id_uindex
		unique (czxid, ctime, batch_id)
);

create index conversion_batch_id_counter_request_queue_is_processed_index
	on conversion_batch_id_counter_request_queue (is_processed);

create table conversion_lambda_metadata_update_queue
(
	item_id int unsigned auto_increment
		primary key,
	chunk_id varchar(64) not null,
	log_type varchar(4) default '' not null,
	uploading_id int unsigned not null,
	uploading_type int unsigned not null,
	line_quantity int not null,
	create_time timestamp default CURRENT_TIMESTAMP not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	is_processed tinyint(1) default 0 null,
	constraint chunk_id
		unique (chunk_id, log_type, uploading_id, uploading_type)
);

create index is_processed
	on conversion_lambda_metadata_update_queue (is_processed);

create table counter_currencies
(
	counter_id int unsigned not null,
	currency_id smallint unsigned not null,
	primary key (counter_id, currency_id)
);

create table counter_features
(
	counter_id int unsigned not null,
    feature_name enum ('offline_calls', 'direct', 'socdem', 'crossdevice', 'webvisor2', 'ua_code', 'offline_visits', 'russian_market', 'target_calls', 'turbo_page', 'turbo_app', 'old_ecommerce', 'ecommerce', 'partner', 'experiment_ab', 'recommendations', 'publishers', 'adfox', 'expenses', 'offline_reach', 'vacuum', 'cdp', 'cross_device_attribution', 'direct_widget', 'statistics_over_site', 'news_enabled_by_classifier') default 'offline_calls'   not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	primary key (counter_id, feature_name)
);

create index feature_name_idx
    on counter_features (feature_name);

create index update_time
	on counter_features (update_time);

create table counter_move_log
(
	log_id bigint unsigned auto_increment
		primary key,
	`current_user` bigint unsigned not null,
	event_time datetime not null,
	from_uid bigint unsigned null,
	to_uid bigint unsigned null,
	counter_id bigint unsigned null
);

create table counter_options
(
	counter_id int unsigned not null
		primary key,
	max_goals int unsigned default 0 not null,
	max_detailed_goals tinyint unsigned default 0 not null,
	max_conditions tinyint unsigned default 0 not null,
	max_filters int(3) unsigned default 0 not null,
	max_operations int(3) unsigned default 0 not null,
	max_logs_api_stored_data_gb int default 10 null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	wv_recp decimal(10,5) null,
	wv_urls varchar(2000) null,
	wv_arch_type varchar(16) null,
	wv_arch_enabled tinyint(1) null,
	wv_load_player enum('proxy', 'on_your_behalf') null,
	wv_version int default 2 null,
	wv2_allow tinyint default 1 null,
	wv2_notify tinyint default 0 null,
	wv_enable_date date null,
	region_details tinyint(1) null,
	markedphones2_params text null,
	max_retargeting_goals int unsigned default 0 not null,
	max_api_segments int unsigned default 0 not null,
	max_interface_segments int unsigned default 0 not null,
	offline_conv_extended_threshold tinyint(1) default 0 not null,
	offline_calls_extended_threshold tinyint(1) default 0 not null,
	offline_visits_extended_threshold tinyint(1) default 0 not null,
	has_csp tinyint(1) default 0 not null,
	alternative_cdn tinyint(1) default 0 not null,
	wv_forms tinyint(1) default 1 null,
	publisher_enabled tinyint(1) null,
	publisher_schema enum('microdata', 'json_ld', 'ontheio', 'schema', 'opengraph', 'linkpulse', 'mediator') null,
	custom_limits tinyint(1) null,
	offline_conv_extended_threshold_enabled_time timestamp null,
	offline_calls_extended_threshold_enabled_time timestamp null,
	c_recp decimal(10,5) default 1.00000 null,
    button_goals tinyint(1) not null default '0',
    form_goals tinyint(1) not null default '0',
	autogoals_enabled tinyint(1) not null default '0',
    hidden_phones text default null,
    use_in_benchmarks tinyint(1) default 1 not null,
    direct_allow_use_goals_without_access tinyint(1) default 0 not null,
    news_enabled_by_user tinyint(1) default 0 not null
);

create index NewIndex1
	on counter_options (update_time);

create index custom_limits
	on counter_options (custom_limits);

create table counter_phones
(
	uid bigint null,
	phone varchar(32) null,
	phone_id bigint null
);

create index uid
	on counter_phones (uid);

create table counter_purchases
(
	date date not null,
	counter_id int unsigned not null,
	count int null,
	primary key (date, counter_id)
);

create table counter_quota
(
	counter_id bigint(10) unsigned not null
		primary key,
	multiplier double unsigned default '2' not null
);

create table counter_visits
(
	counter_id int unsigned not null
		primary key,
	visits bigint unsigned not null,
	last_date date not null
);

create table counter_webmaster_link
(
	counter_id bigint not null,
	domain varchar(128) not null,
	status enum('deleted', 'ok', 'need_metrika_confirm', 'need_webmaster_confirm') default 'deleted' not null,
	update_time datetime not null,
	webmaster_uid bigint null,
	metrika_uid bigint null,
	primary key (counter_id, domain)
);

create table counter_webmaster_link_log
(
	counter_id bigint not null,
	domain varchar(128) not null,
	event_time datetime not null,
	uid bigint not null,
	status_from enum('init', 'deleted', 'ok', 'need_metrika_confirm', 'need_webmaster_confirm') not null,
	status_to enum('deleted', 'ok', 'need_metrika_confirm', 'need_webmaster_confirm') not null
);

create table counters
(
	counter_id int unsigned auto_increment
		primary key,
	owner bigint null,
	name varchar(255) null,
	site varchar(255) null,
	mirrors mediumtext null,
	site_path varchar(255) null,
	mirrors_paths mediumtext null,
	status enum('Active', 'Deleted', 'New') default 'Active' not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	create_time datetime not null,
	external_class tinyint unsigned not null,
	external_cid int unsigned not null,
	enable_monitoring tinyint unsigned default 0 not null,
	enable_sms tinyint unsigned default 0 not null,
	sms_time text null,
	phone varchar(255) null,
	phone_ids varchar(128) null,
	email varchar(255) not null,
	flag enum('', 'yamarket') default '' not null,
	LayerID int(3) unsigned not null,
	MoveLayerID smallint unsigned default 0 not null,
	nano_layer_id int default 0 null,
	code_options text null,
	informer_enabled tinyint(3) default 0 not null,
	informer_type enum('counter', 'informer', 'together') not null,
	informer_color varchar(128) not null,
	informer_indicators varchar(128) not null,
	start_monitoring_date date null,
	time_zone_id int(11) unsigned default 1 not null,
	currency_id smallint unsigned default 643 not null,
	lang char(2) default 'ru' not null,
	widget_settings text null,
	visit_threshold smallint unsigned default 1800 not null,
	wv_visits_limit int(11) unsigned null,
	filter_robots tinyint unsigned default 1 not null,
	counter_rank int default 1 not null,
	max_offline_visit_threshold int unsigned default 21600 not null,
	data_lifetime int unsigned default 86400 not null,
	hide_address tinyint(1) default 0 null,
	gdpr_agreement_accepted tinyint(1) default 0 not null,
	delete_time datetime null,
	source enum('sprav', 'turbodirect', 'partner', 'system') null
);

create index counter_rank
	on counters (counter_rank);

create index counters_name_index
	on counters (name);

create index counters_source_index
	on counters (source);

create index i_counters_createtime
	on counters (create_time);

create index i_counters_owner
	on counters (owner);

create index i_counters_updatetime
	on counters (update_time);

create index i_ext
	on counters (external_cid, external_class);

delimiter |

create trigger layer_validate
	after insert
	on counters
	for each row
BEGIN
    IF NEW.LayerID = 0 THEN
        SIGNAL SQLSTATE '45000'
          SET MESSAGE_TEXT = 'LayerID = 0: you shall not pass';
    END IF;
END;
|

create trigger prohibit_delete_counter
	before delete
	on counters
	for each row
BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'one cannot simply delete a counter';
END;
|

delimiter ;

create table counters_test
(
	counter_id int unsigned default 0 not null
		primary key,
	owner bigint null,
	name varchar(255) null,
	site varchar(255) null,
	mirrors mediumtext null,
	status enum('Active', 'Deleted', 'New') default 'Active' not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	create_time datetime not null,
	external_class tinyint unsigned not null,
	external_cid int unsigned not null,
	enable_monitoring tinyint unsigned default 0 not null,
	enable_sms tinyint unsigned default 0 not null,
	sms_time text null,
	phone varchar(255) null,
	email varchar(255) not null,
	flag enum('', 'yamarket') default '' not null,
	LayerID int(3) unsigned not null,
	MoveLayerID smallint unsigned default 0 not null,
	code_options text null,
	informer_enabled tinyint(3) default 0 not null,
	informer_type enum('counter', 'informer', 'together') not null,
	informer_color varchar(128) not null,
	informer_indicators varchar(128) not null,
	start_monitoring_date date null,
	time_zone_id int(11) unsigned default 1 not null,
	lang char(2) default 'ru' not null,
	widget_settings text null,
	visit_threshold smallint unsigned default 1800 not null,
	wv_visits_limit int(11) unsigned default 1000 not null,
	filter_robots tinyint unsigned default 1 not null
);

create table countries
(
	id int unsigned not null
		primary key,
	code varchar(3) null,
	name varchar(255) null,
	sync_holidays tinyint(1) default 0 not null,
	constraint code
		unique (code)
);

create table csp_alive_domains
(
	domain varchar(255) default '' not null,
	processed tinyint(1) default 0 null,
	user_agent_code varchar(30) default 'robot' not null,
	primary key (domain, user_agent_code)
);

create table csp_directives
(
	id int unsigned auto_increment
		primary key,
	domain varchar(255) default '' not null,
	user_agent_code varchar(30) default 'robot' not null,
	directive text not null
);

create table csp_domains
(
	domain varchar(255) default '' not null,
	http_code int(10) null,
	has_csp int(1) null,
	user_agent_code varchar(30) default 'robot' not null,
	primary key (domain, user_agent_code)
);

create table currency
(
	id smallint unsigned not null
		primary key,
	code char(3) not null,
	name varchar(128) not null,
	`order` smallint unsigned default 0 not null,
	constraint code
		unique (code)
);

create table currency_rates
(
	currency_code char(3) not null,
	rate_date date not null,
	original_rate_date date null,
	time_zone tinytext null,
	time_zone_id smallint unsigned null,
	from_usd_rate decimal(15,6) null,
	add_time timestamp default CURRENT_TIMESTAMP not null,
	rate_source tinytext not null,
	rate_source_type enum('prolonged', 'refs_paysys') default 'refs_paysys' not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	primary key (currency_code, rate_date)
);

create table delegate_quota
(
	uid bigint(10) unsigned not null
		primary key,
	multiplier double unsigned default '2' not null
);

create table dismissed_notifications
(
	uid bigint not null,
	notification_id bigint not null,
	primary key (uid, notification_id)
);

create table domain_counters
(
	counter_id int(10) default 0 not null,
	domain varchar(255) default '' not null,
	primary key (counter_id, domain)
);

create index domain
	on domain_counters (domain);

create table experiment_ab_REMOVE
(
	experiment_id bigint unsigned auto_increment
		primary key,
	owner_id bigint unsigned not null,
	counter_ids varchar(128) not null,
	name varchar(64) not null,
	salt bigint unsigned not null,
	status enum('active', 'deleted') default 'active' not null,
	create_time datetime not null,
	update_time datetime not null,
	serial int not null,
	delete_time datetime null
);

create table experiment_csp_domains
(
	domain varchar(255) default '' not null,
	http_code int(10) null,
	user_agent varchar(200) default '' not null,
	has_csp int(1) null,
	primary key (domain, user_agent)
);

create table external_counters
(
	external_cid int unsigned not null
		primary key,
	id int unsigned not null,
	title varchar(255) not null
);

create table gdpr_cookies
(
	service_id bigint not null,
	cookie_name varchar(128) not null,
	cookie_type varchar(16) not null,
	cookie_ttl bigint default 0 not null,
	cookie_descr varchar(2048) not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	primary key (service_id, cookie_name)
);

create table gdpr_services
(
	service_id bigint not null
		primary key,
	service_name varchar(32) not null
);

create table geo_points
(
	id int unsigned auto_increment
		primary key,
	permalink bigint unsigned null,
	counter_id int unsigned not null,
	latitude varchar(20) not null,
	longitude varchar(20) not null,
	comment varchar(255) null,
	region_id int null,
	region_name varchar(128) null,
	create_time datetime not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	deleted tinyint(1) default 0 null
);

create index counter_id
	on geo_points (counter_id);

create index counter_id_2
	on geo_points (counter_id, latitude, longitude);

create table geo_points_dump
(
	id int unsigned auto_increment
		primary key,
	permalink bigint unsigned null,
	counter_id int unsigned not null,
	latitude varchar(20) not null,
	longitude varchar(20) not null,
	comment varchar(255) null,
	region_id int null,
	region_name varchar(128) null,
	create_time datetime not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	deleted tinyint(1) default 0 null
);

create index counter_id
	on geo_points_dump (counter_id);

create index counter_id_2
	on geo_points_dump (counter_id, latitude, longitude);

create table grant_quota
(
	counter_id bigint(10) unsigned not null
		primary key,
	multiplier double unsigned default '2' not null
);

create table grant_requests
(
	object_type enum('counter', 'delegate') null,
	object_id varchar(255) default '' not null,
	rw tinyint(1) null,
	requestor_login varchar(255) default '' not null,
	requestor_uid bigint unsigned not null,
	requestor_email varchar(255) null,
	send_sms tinyint(1) null,
	comment varchar(255) null,
	mdate timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	object_owner varchar(255) null,
	object_owner_uid bigint unsigned not null,
	service_name varchar(32) null,
	lang varchar(4) default 'ru' null,
	primary key (object_id, requestor_login)
);

create index object_owner_uid_idx
	on grant_requests (object_owner_uid);

create index owner
	on grant_requests (object_owner);

create table guest_networks
(
	address varchar(255) not null
);

create table holidays
(
	id int unsigned auto_increment
		primary key,
	country_id int unsigned null,
	date date null,
	type enum('HOLIDAY', 'DAY_OFF_TRANSFER', 'WORKDAY_TRANSFER') null,
	transferred_date date null,
	name varchar(255) null
);

create table icons
(
	id bigint auto_increment
		primary key,
	duri varchar(8192) null
);

create table internal_networks
(
	address varchar(255) not null
);

create table ip_quota
(
	ip varchar(150) not null
		primary key,
	multiplier double unsigned default '2' not null
);

create table labels
(
	id int(11) unsigned auto_increment
		primary key,
	serial int unsigned default 0 not null,
	uid bigint unsigned not null,
	label varchar(255) not null,
	status enum('active', 'deleted') default 'active' not null
);

create index uid
	on labels (uid);

create table labels_to_counters
(
	label_id int(11) unsigned not null,
	counter_id int(11) unsigned not null,
	primary key (counter_id, label_id)
);

create table last_dd
(
	uid int not null,
	max_date date null
);

create table log_request_parts
(
	request_id int(11) unsigned not null,
	part_number int(11) unsigned not null,
	mds_key varchar(100) not null,
	size bigint unsigned not null,
	uploading_duration int(11) unsigned not null,
	primary key (request_id, part_number)
);

create table log_requests
(
	request_id int(11) unsigned auto_increment
		primary key,
	owner_id bigint unsigned null,
	counter_id int(11) unsigned not null,
	layer_id int(11) unsigned not null,
	source enum('hits', 'visits') not null,
	date1 varchar(20) not null,
	date2 varchar(20) not null,
	fields varchar(3000) not null,
	expected_size bigint unsigned not null,
	status enum('created', 'canceled', 'processed', 'cleaned_by_user', 'cleaned_automatically_as_too_old', 'processing_failed') not null,
	size bigint unsigned null,
	create_time timestamp default CURRENT_TIMESTAMP not null,
	processing_time timestamp null,
	cleaning_time timestamp null,
	partitioning_type enum('sample', 'shard_mtgiga') null,
	parts_count int(10) null,
	shards_count int(10) null,
	error_message varchar(200) null,
	error_trace varchar(2000) null,
	attribution enum('FIRST', 'LAST', 'LASTSIGN', 'LAST_YANDEX_DIRECT_CLICK') null
);

create index counter_id
	on log_requests (counter_id);

create table markedphones2_bonus
(
	id int auto_increment
		primary key,
	numberodays int not null,
	from_uid bigint not null,
	to_uid bigint not null,
	comment varchar(255) not null,
	create_time timestamp default CURRENT_TIMESTAMP not null
);

create table markedphones2_cdr_dump
(
	counter_id int not null,
	provider_id int not null,
	call_id int(11) unsigned not null,
	track_id int not null,
	date date not null,
	ts datetime not null,
	hold_duration int not null,
	talk_duration int not null,
	ani varchar(64) charset latin1 null,
	un varchar(32) charset latin1 not null,
	dn varchar(32) charset latin1 not null,
	conditions text null,
	tree_path_b64 text charset latin1 not null,
	layer_id int not null,
	primary key (provider_id, call_id)
);

create index call_id
	on markedphones2_cdr_dump (call_id);

create index counter_id
	on markedphones2_cdr_dump (counter_id);

create index date
	on markedphones2_cdr_dump (date);

create index layer_id
	on markedphones2_cdr_dump (layer_id);

create index track_id
	on markedphones2_cdr_dump (track_id);

create index ts
	on markedphones2_cdr_dump (ts);

create table markedphones2_cdr_dump2
(
	call_id bigint not null,
	provider_id int not null,
	ani varchar(255) null,
	counter_id int null,
	dn varchar(255) null,
	hold_duration int null,
	talk_duration int null,
	ts datetime null,
	track_id int null,
	un varchar(255) null,
	primary key (call_id, provider_id)
);

create index ts
	on markedphones2_cdr_dump2 (ts);

create table markedphones2_cdr_dump3
(
	counter_id int not null,
	provider_id int not null,
	call_id int(11) unsigned not null,
	track_id int not null,
	date date not null,
	ts datetime not null,
	hold_duration int not null,
	talk_duration int not null,
	ani varchar(64) charset latin1 null,
	un varchar(32) charset latin1 not null,
	dn varchar(32) charset latin1 not null,
	conditions text null,
	tree_path_b64 text charset latin1 not null,
	layer_id int not null,
	primary key (counter_id, provider_id, call_id)
);

create index dc
	on markedphones2_cdr_dump3 (counter_id, date);

create index pc
	on markedphones2_cdr_dump3 (provider_id, call_id);

create table markedphones2_cdr_dump_layers
(
	layer_id int not null
		primary key,
	date date not null
)
charset=latin1;

create table markedphones2_cities
(
	country varchar(4) not null,
	code varchar(8) not null,
	city varchar(256) not null,
	timezone int not null,
	primary key (country, code)
);

create table markedphones2_debits_by_orders
(
	uid bigint not null,
	date date not null,
	order_id int not null,
	numberodays int not null,
	primary key (uid, date, order_id)
);

create table markedphones2_debits_by_tracks
(
	uid bigint not null,
	date date not null,
	track_id int not null,
	phone_id int not null,
	primary key (uid, date, track_id)
);

create table markedphones2_debits_daily
(
	uid bigint not null,
	date date not null,
	phones_max int not null,
	phones_end int not null,
	numberodays_end int default 0 not null comment 'остаток номеродней всего',
	money_end int default 0 not null comment 'остаток оплаченных рублей',
	bonus_end int default 0 not null comment 'остаток бонусных рублей',
	debit_numberodays_goods int default 0 not null comment 'расход оплаченных номеродней',
	debit_numberodays_bonus int default 0 not null comment 'расход бонусных номеродней',
	debit_money_goods int default 0 not null comment 'расход оплаченных рублей',
	debit_money_bonus int default 0 not null comment 'расход бонусных рублей',
	numberodays_end_goods int default 0 not null comment 'остаток оплаченных номеродней',
	numberodays_end_bonus int default 0 not null comment 'остаток бонусных номеродней',
	primary key (uid, date)
);

create table markedphones2_goods
(
	goods_id int not null
		primary key,
	title varchar(512) null,
	cost int not null,
	priority int not null
);

create table markedphones2_last_billdate
(
	uid bigint default 0 not null
		primary key,
	last_bill_date date not null
);

create table markedphones2_layers
(
	layer_id int unsigned not null,
	provider_id int not null,
	last_cdr_id int null,
	primary key (layer_id, provider_id)
);

create table markedphones2_nopoollog
(
	timestamp datetime null,
	date date null,
	uid bigint not null,
	counter_id int null,
	track text null
);

create index date
	on markedphones2_nopoollog (date);

create index timestamp
	on markedphones2_nopoollog (timestamp);

create index uid
	on markedphones2_nopoollog (uid);

create table markedphones2_orders
(
	order_id int auto_increment
		primary key,
	uid bigint not null,
	goods_id int not null,
	numberodays_purchased int not null,
	create_date datetime not null,
	numberodays_used int not null,
	notify_num bigint not null
);

create index create_date
	on markedphones2_orders (create_date);

create index uid
	on markedphones2_orders (uid);

create table markedphones2_orders_history
(
	order_id int not null,
	received_ts timestamp default CURRENT_TIMESTAMP not null,
	numberodays int not null,
	numberodays_delta int not null,
	notify_num bigint not null,
	money_recive float not null
);

create index notify_num
	on markedphones2_orders_history (notify_num);

create index order_received
	on markedphones2_orders_history (order_id, received_ts);

create table markedphones2_orders_log
(
	id int auto_increment,
	bd datetime(3) default '1000-01-01 00:00:00.000' not null,
	ed datetime(3) default '9999-12-31 23:59:59.999' not null,
	uid bigint not null,
	goods_id int not null,
	numberodays_purchased int not null,
	create_date datetime not null,
	numberodays_used int not null,
	notify_num bigint not null,
	primary key (id, bd, ed)
);

create table markedphones2_phones
(
	phone_id int auto_increment
		primary key,
	uid bigint null,
	provider_id int not null,
	un_country varchar(4) not null,
	un_code varchar(8) not null,
	un_phone varchar(16) not null,
	dn varchar(2048) null,
	active tinyint(1) default 1 not null,
	need_update tinyint(1) default 1 null,
	link_ts datetime null,
	unlink_ts datetime null,
	release_ts datetime null,
	used datetime null
);

create table markedphones2_phones_comstar
(
	phone_id int not null,
	comstar_id int not null
		primary key,
	last_stat datetime null
);

create index phone_id
	on markedphones2_phones_comstar (phone_id);

create table markedphones2_phones_lost
(
	phone_id int default 0 not null,
	uid bigint null,
	provider_id int not null,
	un_country varchar(4) not null,
	un_code varchar(8) not null,
	un_phone varchar(16) not null,
	dn varchar(2048) null,
	active tinyint(1) default 1 not null,
	need_update tinyint(1) default 1 null,
	link_ts datetime null,
	unlink_ts datetime null,
	release_ts datetime null,
	used datetime null
);

create table markedphones2_poollog
(
	timestamp datetime not null,
	date date not null,
	un_country varchar(4) not null,
	un_code varchar(8) not null,
	fresh int not null,
	used int not null,
	settling int not null,
	in_use int not null,
	total int not null,
	disabled int not null,
	primary key (timestamp, un_country, un_code)
);

create table markedphones2_poollog2
(
	timestamp datetime not null,
	date date not null,
	un_country varchar(4) not null,
	un_code varchar(8) not null,
	provider_id int not null,
	fresh int not null,
	used int not null,
	settling int not null,
	in_use int not null,
	total int not null,
	disabled int not null,
	primary key (timestamp, un_country, un_code, provider_id)
);

create table markedphones2_promo
(
	code_id int auto_increment
		primary key,
	code varchar(16) not null,
	tag varchar(128) null,
	numberodays int not null,
	create_ts timestamp default CURRENT_TIMESTAMP not null,
	expire_ts datetime not null,
	uid bigint null,
	activation_ts datetime null,
	comment varchar(1024) null,
	constraint code
		unique (code)
);

create table markedphones2_prov_redir
(
	provider_id int not null,
	redir_id int not null,
	weight int unsigned default 0 not null,
	primary key (provider_id, redir_id)
);

create index provider_id
	on markedphones2_prov_redir (provider_id);

create index redir_id
	on markedphones2_prov_redir (redir_id);

create table markedphones2_providers
(
	provider_id int not null
		primary key,
	name varchar(256) null,
	api int null,
	url varchar(256) null,
	realm varchar(256) null,
	user varchar(256) null,
	passwd varchar(256) null,
	active enum('on', 'off') default 'on' null,
	max_id int null,
	cdr_batch_size int(11) unsigned default 2000 not null,
	last_update datetime null
);

create index api
	on markedphones2_providers (api);

create table markedphones2_redirections
(
	redir_id int not null
		primary key,
	country varchar(4) not null,
	un_code varchar(8) not null,
	dn_code varchar(8) not null
);

create index dn_code
	on markedphones2_redirections (dn_code);

create index un_code
	on markedphones2_redirections (un_code);

create table markedphones2_tracks
(
	track_id int auto_increment
		primary key,
	uid bigint not null,
	counter_id int not null,
	phone_id int not null,
	dns_order enum('random', 'sequent') not null,
	conditions text null,
	substs text null,
	status enum('active', 'hold', 'quarantine', 'expired', 'replaced') not null,
	constraint phone_id
		unique (phone_id)
);

create index uid
	on markedphones2_tracks (uid);

create table markedphones2_tracks_archive
(
	track_id int not null
		primary key,
	uid bigint not null,
	counter_id int not null,
	visible tinyint(1) null,
	data mediumtext null,
	add_ts timestamp default CURRENT_TIMESTAMP not null
);

create index add_ts
	on markedphones2_tracks_archive (add_ts);

create index counter_idx
	on markedphones2_tracks_archive (counter_id);

create index uid
	on markedphones2_tracks_archive (uid);

create table markedphones2_tracks_archive_joined
(
	track_id int not null
		primary key,
	uid bigint not null,
	counter_id int not null,
	dns_order enum('random', 'sequent') not null,
	conditions text null,
	substs text null,
	phone_id int not null,
	provider_id int not null,
	un_country varchar(4) not null,
	un_code varchar(8) not null,
	un_phone varchar(16) not null,
	dn varchar(2048) null,
	add_ts timestamp default CURRENT_TIMESTAMP not null
);

create index counter_idx
	on markedphones2_tracks_archive_joined (counter_id);

create index phone_id
	on markedphones2_tracks_archive_joined (phone_id);

create index uid
	on markedphones2_tracks_archive_joined (uid);

create table markedphones2_tracks_history
(
	track_id int not null,
	status enum('active', 'hold', 'quarantine', 'expired', 'replaced') not null,
	change_ts timestamp default CURRENT_TIMESTAMP not null,
	counter_id int not null,
	action_by_uid bigint null,
	constraint track_id_2
		unique (track_id, change_ts)
);

create index change_ts
	on markedphones2_tracks_history (change_ts);

create index track_id
	on markedphones2_tracks_history (track_id);

create table markedphones2_uidslog
(
	timestamp datetime not null
		primary key,
	date date not null,
	total int not null,
	active int not null,
	hold int not null
);

create table mobile_phone_images
(
	vendor int default 0 not null,
	model varchar(32) default '' not null,
	resolution varchar(32) default '*' not null,
	image_id varchar(42) null,
	device_width int null,
	device_height int null,
	landscape_width int null,
	landscape_height int null,
	landscape_left int null,
	landscape_top int null,
	portrait_width int null,
	portrait_height int null,
	portrait_left int null,
	portrait_top int null,
	primary key (vendor, model, resolution)
);

create table monitoring2_resolver_log
(
	dayNumber int not null,
	domain varchar(200) not null,
	check_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	daemon_id varchar(16) null,
	resp_time int null,
	ip_addresses int null,
	primary key (domain, check_time, dayNumber)
);

create table notification_localizations
(
	notification_id bigint not null,
	language char(2) not null,
	title varchar(256) not null,
	body varchar(4096) null,
	primary key (notification_id, language)
);

create table notifications
(
	id bigint auto_increment
		primary key,
	type enum('info', 'update', 'critical') not null,
	alert tinyint(1) null,
	pending tinyint(1) null,
	start_time datetime not null,
	end_time datetime not null,
	icon_id bigint null,
	status enum('active', 'deleted') default 'active' not null,
	create_time timestamp default CURRENT_TIMESTAMP not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	uid bigint default 0 not null
);

create index start_time
	on notifications (start_time, end_time);

create table notifications_scopes
(
	notification_id bigint not null,
	scope_id bigint not null,
	primary key (notification_id, scope_id)
);

create table offline_conversion_duplicate_request_queue
(
	id varchar(64) not null
		primary key,
	status varchar(64) default 'new' not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP
);

create table offline_conversion_uploadings
(
	uploading_id int unsigned auto_increment
		primary key,
	counter_id int unsigned not null,
	layer_id int unsigned not null,
	create_time timestamp default CURRENT_TIMESTAMP not null,
	processed_time timestamp null,
	client_id_type enum('USER_ID', 'CLIENT_ID', 'YCLID') null,
	status enum('UPLOADED', 'PROCESSED', 'LINKAGE_FAILURE', 'EXPORTED', 'MATCHED', 'PREPARED') null,
	comment varchar(255) null,
	repository_chunk_id varchar(100) null,
	source_quantity int null,
	line_quantity int null,
	linked_quantity int null,
	processed_quantity int null,
	goal_not_found_quantity int null,
	user_not_found_quantity int null,
	static_calls_quantity int null,
	dynamic_calls_quantity int null,
	duplicate_quantity int default 0 null,
	min_event_time timestamp null,
	max_event_time timestamp null,
	chunks_quantity int null,
	chunks_meta text null,
	type enum('BASIC', 'CALLS') null
);

create index `index`
	on offline_conversion_uploadings (counter_id);

create index layer_id_status
	on offline_conversion_uploadings (layer_id, status);

create index status
	on offline_conversion_uploadings (status);

create table old_counter_stat
(
	counter_id int unsigned not null
		primary key,
	today_visits int unsigned not null,
	today_hits int unsigned not null,
	today_uniques int unsigned not null,
	week_visits varchar(128) not null,
	week_hits varchar(128) not null,
	week_uniques varchar(128) not null,
	prev24hours_visits int(10) not null,
	prev24hours_hits int(10) not null,
	prev24hours_uniques int(10) not null,
	last24hours_visits int(10) not null,
	last24hours_hits int(10) not null,
	last24hours_uniques int(10) not null,
	last_date date not null,
	last2hours_visits int(10) null
);

create table old_guest_networks
(
	address varchar(255) not null
);

create table old_internal_networks
(
	address varchar(255) not null
);

create table old_sprav_company
(
	company_id bigint not null
		primary key,
	name varchar(128) null,
	address varchar(512) null,
	region_id int null,
	region_name varchar(64) default '' null,
	country_id int null,
	latitude varchar(16) null,
	longitude varchar(16) null,
	permalink bigint null,
	commit_unixtime bigint null,
	type varchar(32) null
);

create index permalink
	on old_sprav_company (permalink);

create table old_sprav_company_to_rubric
(
	company_id bigint not null,
	company_permalink bigint not null,
	rubric_id bigint not null,
	rubric_permalink bigint not null,
	is_main tinyint null,
	primary key (company_id, rubric_id)
);

create index company_permalink
	on old_sprav_company_to_rubric (company_permalink, rubric_permalink);

create table old_sprav_company_to_url
(
	id bigint not null,
	permalink bigint null,
	country_id int null,
	value varchar(512) null,
	type varchar(32) null,
	hide tinyint null
);

create index id
	on old_sprav_company_to_url (id);

create index permalink
	on old_sprav_company_to_url (permalink);

create index value
	on old_sprav_company_to_url (value);

create table old_sprav_domain_count
(
	domain varchar(128) default '' not null
		primary key,
	companies int null
);

create table old_sprav_rubric
(
	id bigint not null
		primary key,
	name varchar(64) null,
	permalink bigint null,
	commit_unixtime bigint null,
	status varchar(20) null
);

create table old_sprav_rubric_count
(
	domain varchar(128) default '' not null,
	rubric_id bigint default 0 not null,
	companies int null,
	primary key (domain, rubric_id)
);

create table parallel_requests_quota
(
	uid bigint unsigned not null,
	source enum('api', 'interface') not null,
	count bigint unsigned not null,
	primary key (uid, source)
);

create table partner_tmp
(
	counter_id int unsigned not null
		primary key,
	page_id int unsigned null
);

create table partner_tmp2
(
	counter_id int unsigned not null,
	page_id int unsigned null
);

create table partner_tmp3
(
	counter_id int unsigned not null,
	page_id int unsigned null
);

create table project_stat
(
	stat_date date not null
		primary key,
	sessions int unsigned not null,
	sessions_binded int unsigned not null,
	clicks int unsigned not null,
	clicks_binded int unsigned not null,
	hits int unsigned not null,
	hits_metrics int unsigned not null,
	active_counters int unsigned not null,
	checked_counters int unsigned not null,
	new_counters int unsigned not null,
	created_counters int unsigned not null,
	active_logins int unsigned not null
)
charset=cp1251;

create table project_stat_update
(
	stat_date date not null
		primary key,
	update_time datetime not null
)
charset=cp1251;

create index ut
	on project_stat_update (update_time);

create table properties
(
	name varchar(100) default '' not null
		primary key,
	value varchar(100) null
);

create table proxy_options
(
	id bigint auto_increment
		primary key,
	code varchar(32) not null,
	options varchar(1000) not null,
	last_modified timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP
);

create index code
	on proxy_options (code);

create index lmidx
	on proxy_options (last_modified);

create index opt_idx
	on proxy_options (options);

create table proxy_tokens
(
	token char(36) collate ascii_bin default '' not null
		primary key,
	domain varchar(255) collate utf8_bin null,
	uid bigint null,
	usage_count int default 0 null,
	last_modified timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	created timestamp default CURRENT_TIMESTAMP not null,
	constraint uid
		unique (uid, domain)
);

create table pvl_domains
(
	counter_id int unsigned not null,
	domain varchar(64) not null,
	primary key (counter_id, domain)
);

create table pvl_points
(
	point_id int unsigned auto_increment
		primary key,
	counter_id int unsigned not null,
	permalink bigint not null,
	latitude varchar(20) not null,
	longitude varchar(20) not null,
	name varchar(128) null,
	comment varchar(255) null,
	region_id int null,
	region_name varchar(64) default '' null,
	create_time datetime not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	deleted tinyint(1) default 0 null
);

create index counter_id_2
	on pvl_points (counter_id, permalink);

create index permalink
	on pvl_points (permalink);

create table pvl_rubrics
(
	counter_id int unsigned not null,
	rubric_id bigint not null,
	primary key (counter_id, rubric_id)
);

create table radar_subscriptions
(
	subscription_id int unsigned auto_increment
		primary key,
	counter_id int unsigned not null,
	subscription blob not null,
	measure varchar(50) not null,
	changes tinyint(1) not null,
	`group` enum('day', 'week', 'month', 'all') not null,
	status enum('Active', 'Deleted') default 'Active' not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP
);

create table report_executions
(
	id int unsigned auto_increment
		primary key,
	report_order_id int unsigned not null,
	counter_id int unsigned not null,
	create_time timestamp default CURRENT_TIMESTAMP not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	deleted tinyint(1) default 0 not null,
	initial_exec_time timestamp null,
	exec_time timestamp null,
	timeouts_amount int default 0 not null,
	complete_time timestamp null,
	status enum('NEW', 'IN_PROGRESS', 'COMPLETE', 'FAILED') null,
	failure_reason enum('TIMEOUT', 'MEMORY_LIMIT_EXCEEDED', 'COUNTER_NOT_FOUND', 'OWNER_NOT_FOUND', 'PERMISSION_DENIED', 'INVALID_CONSTRUCTOR_PARAMS', 'TOO_COMPLEX_QUERY') null,
	date1 date null,
	date2 date null,
	mds_s3_bucket_name varchar(255) null,
	result_total_static_rows bigint null,
	result_total_dynamic_rows bigint null,
	execution_time bigint null,
	execution_duration bigint null,
	email_notification_sent tinyint(1) null,
	email_notification_time timestamp null
);

create index counter_id
	on report_executions (counter_id);

create index report_order_id
	on report_executions (report_order_id);

create index status
	on report_executions (status);

create index status_email_notification_sent
	on report_executions (status, email_notification_sent);

create index status_exec_time
	on report_executions (status, exec_time);

create table report_orders
(
	id int unsigned auto_increment
		primary key,
	counter_id int unsigned not null,
	owner_id bigint unsigned not null,
	name varchar(255) null,
	type enum('SINGLE', 'REGULAR') null,
	create_time timestamp default CURRENT_TIMESTAMP not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	deleted tinyint(1) default 0 not null,
	status enum('ACTIVE', 'INACTIVE') null,
	inactivation_reason enum('MANUAL', 'ENDED', 'TOO_MANY_TIMEOUTS', 'MEMORY_LIMIT_EXCEEDED', 'COUNTER_NOT_FOUND', 'OWNER_NOT_FOUND', 'PERMISSION_DENIED', 'INVALID_CONSTRUCTOR_PARAMS', 'TOO_COMPLEX_QUERY') null,
	next_exec_time timestamp null,
	date1 date null,
	date2 date null,
	frequency enum('DAILY', 'WEEKLY', 'MONTHLY') null,
	recipient_emails varchar(1023) null,
	end_date date null,
	preset varchar(255) null,
	metrics text null,
	dimensions text null,
	filters text null,
	sort text null,
	dynamic_metric varchar(255) null,
	include_undefined tinyint(1) null,
	with_confidence tinyint(1) null,
	exclude_insignificant tinyint(1) null,
	confidence_level double null,
	max_deviation double null,
	`group` varchar(255) null,
	direct_client_logins varchar(1023) null,
	other_params text null,
	lang varchar(255) null,
	request_domain varchar(255) null,
	target_table varchar(255) null
);

create index counter_id
	on report_orders (counter_id);

create index status
	on report_orders (status);

create index status_next_exec_time
	on report_orders (status, next_exec_time);

create table report_segments
(
	segment_id int unsigned auto_increment
		primary key,
	counter_id int unsigned not null,
	report_name varchar(32) not null,
	data mediumtext not null,
	name mediumtext not null,
	create_time datetime not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	deleted tinyint default 0 not null
);

create index IX_counter
	on report_segments (counter_id, report_name);

create table report_segments_backup
(
	segment_id int unsigned default 0 not null,
	counter_id int unsigned not null,
	report_name varchar(32) not null,
	data mediumtext not null,
	name mediumtext not null,
	create_time datetime not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	deleted tinyint default 0 not null
);

create table retargeting_segments
(
	segment_id int unsigned default 0 not null
);

create table scopes
(
	id bigint auto_increment
		primary key,
	name varchar(128) null,
	constraint name
		unique (name)
);

create table segment_ab_REMOVE
(
	segment_id bigint unsigned auto_increment
		primary key,
	experiment_id bigint unsigned not null,
	name varchar(64) not null,
	bucket_start int unsigned not null,
	bucket_end int unsigned not null,
	create_time datetime not null,
	update_time datetime not null
);

create table segment_users
(
	segment_id int unsigned not null
		primary key,
	week_users bigint unsigned not null,
	month_users bigint unsigned not null,
	week_segment_users bigint unsigned not null,
	month_segment_users bigint unsigned not null,
	last_date date not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP
);

create table segment_visits
(
	segment_id int unsigned not null,
	date date not null,
	visits bigint unsigned not null,
	primary key (segment_id, date)
);

create table segments
(
	segment_id int unsigned auto_increment
		primary key,
	counter_id int unsigned not null,
	owner bigint not null,
	name varchar(255) null,
	expression mediumtext null,
	expression_version int unsigned not null default 1,
	status enum('active', 'deleted') default 'active' not null,
	is_retargeting tinyint(1) default 0 not null,
	direct_retargeting tinyint(1) default 0 not null,
	display_retargeting tinyint(1) default 0 not null,
	adfox_retargeting tinyint(1) default 0 not null,
	banana_retargeting tinyint(1) default 0 not null,
	geoadv_retargeting tinyint(1) unsigned default 0 not null,
	zen_retargeting tinyint(1) unsigned default 0 not null,
    disk_retargeting tinyint(1) unsigned default 0 not null,
	create_time timestamp default CURRENT_TIMESTAMP not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	segment_source enum('interface', 'api') default 'interface' not null,
	segment_retargeting enum('not_allow', 'allow', 'need_recalculation') default 'need_recalculation' not null,
	streamable tinyint(1) default 0 not null,
	streamability_features set('decomposition', 'simple_functions', 'dicts_functions', 'hard_functions', 'visits', 'hits') default '' not null
);

create index counter_id
	on conv_main.segments (counter_id);

create index create_time
	on conv_main.segments (create_time);

create table segments_expression_history
(
	segment_id int unsigned not null,
	version int unsigned not null,
	expression mediumtext null,
	create_time timestamp default CURRENT_TIMESTAMP not null,
	primary key (segment_id, version)
);

create table segments_queue
(
	id bigint unsigned auto_increment
		primary key,
	segment_id int unsigned not null,
	add_time timestamp default CURRENT_TIMESTAMP not null
);

create table seq_test
(
	id bigint auto_increment
		primary key,
	`when` timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	max_mod_1 bigint null,
	max_mod_2 bigint null
);

create table service_quota
(
	service_id bigint(10) not null
		primary key,
	multiplier double unsigned default '2' not null
);

create table share_services
(
	id varchar(64) not null
		primary key,
	title varchar(64) not null,
	title_js_escapes varchar(255) null
);

create table sprav_company
(
	company_id bigint not null
		primary key,
	name varchar(128) null,
	address varchar(512) null,
	region_id int null,
	region_name varchar(64) default '' null,
	country_id int null,
	latitude varchar(16) null,
	longitude varchar(16) null,
	permalink bigint null,
	commit_unixtime bigint null,
	type varchar(32) null
);

create index permalink
	on sprav_company (permalink);

create table sprav_company_to_rubric
(
	company_id bigint not null,
	company_permalink bigint not null,
	rubric_id bigint not null,
	rubric_permalink bigint not null,
	is_main tinyint null,
	primary key (company_id, rubric_id)
);

create index company_permalink
	on sprav_company_to_rubric (company_permalink, rubric_permalink);

create table sprav_company_to_url
(
	id bigint not null,
	permalink bigint null,
	country_id int null,
	value varchar(512) null,
	type varchar(32) null,
	hide tinyint null
);

create index id
	on sprav_company_to_url (id);

create index permalink
	on sprav_company_to_url (permalink);

create index value
	on sprav_company_to_url (value);

create table sprav_domain_count
(
	domain varchar(128) default '' not null
		primary key,
	companies int null
);

create table sprav_rubric
(
	id bigint not null
		primary key,
	name varchar(64) null,
	permalink bigint null,
	commit_unixtime bigint null,
	status varchar(20) null
);

create table sprav_rubric_count
(
	domain varchar(128) default '' not null,
	rubric_id bigint default 0 not null,
	companies int null,
	primary key (domain, rubric_id)
);

create table test_uids
(
	uid bigint unsigned not null
);

create table th_double
(
	track_id int not null,
	status enum('active', 'hold', 'quarantine', 'expired', 'replaced') not null,
	change_ts timestamp default CURRENT_TIMESTAMP not null,
	counter_id int not null,
	action_by_uid bigint null
);

create table time_zones
(
	time_zone_id smallint unsigned default 0 not null
		primary key,
	name varchar(255) default '' not null,
	used_order smallint unsigned default 0 not null,
	user_tz tinyint(1) default 0 not null,
	country_id int unsigned null
);


create table tmp_c
(
	counter_id int unsigned not null
);

create table tmp_campaigns
(
	cid bigint unsigned not null,
	owner bigint unsigned not null,
	primary key (owner, cid)
)
comment 'для очтета по директу';

create index cid_idx
	on tmp_campaigns (cid);

create table tmp_counters_for_wv2_20171212
(
	counter_id int unsigned default 0 not null
);

create table tmp_counters_for_wv2_20171212_no_notify
(
	counter_id int unsigned default 0 not null
		primary key
);

create table tmp_counters_for_wv2_20171212_notify
(
	counter_id int unsigned default 0 not null
		primary key
);

create table tmp_counters_for_wv2_allow_20180806
(
	counter_id int unsigned not null
);

create table tmp_counters_for_wv2_allow_20180808
(
	counter_id int unsigned not null
		primary key
);

create table tmp_counters_for_wv2_allow_20180810
(
	counter_id int unsigned not null
		primary key
);

create table tmp_counters_for_wv2_allow_20180813
(
	counter_id int unsigned not null
		primary key
);

create table tmp_counters_not_for_wv2_20180116
(
	counter_id int unsigned default 0 not null
		primary key
);

create table tmp_counters_with_visor_enabled_20190912
(
	counter_id int not null
		primary key
);

create table tmp_geo_points
(
	longitude varchar(20) not null,
	latitude varchar(20) not null,
	counter_id int unsigned not null
);

create index longitude
	on tmp_geo_points (longitude, latitude, counter_id);

create table tmp_layers
(
	counter_id int unsigned default 0 not null,
	LayerID int(3) unsigned not null
);

create table tmp_phone_data
(
	uid bigint null,
	email varchar(64) null,
	counter bigint null,
	phone varchar(32) null,
	phone_id varchar(32) null
);

create index counter
	on tmp_phone_data (counter);

create table tmp_ts
(
	track_id int not null,
	mct timestamp null
);

create table tmp_uids
(
	uid bigint null,
	login varchar(64) null
);

create table tmp_vacuum_goals
(
	goal_id int unsigned not null
		primary key
);

create table tmp_yalogins
(
	staff varchar(64) null,
	yalogin varchar(64) null
);

create table top_metrika_domains
(
	counter_id int not null
		primary key,
	domain varchar(128) null
);

create table trusted_addresses
(
	data varchar(64) not null,
	type enum('ip', 'network', 'host', 'conductor', 'racktables', 'qloud') not null,
	comment varchar(255) null,
	token varchar(255) not null,
	create_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP
);

create table tvm_internal_users
(
	service_id int(11) unsigned not null,
	environment enum('production', 'testing') not null,
	uid bigint unsigned not null,
	service_name varchar(255) not null,
	status enum('active', 'archive') default 'active' null,
	comment varchar(255) null,
	create_time timestamp default CURRENT_TIMESTAMP not null,
	primary key (service_id, environment, uid)
);

create index uid
	on tvm_internal_users (uid);

create table tvm_internal_users_quotas
(
	uid bigint unsigned not null,
	quota_type varchar(255) default '' not null,
	quota_limit bigint unsigned not null,
	quota_used bigint default 0 null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	primary key (uid, quota_type)
);

create table tvm_service_to_uid
(
	service_id int(11) unsigned not null,
	uid bigint unsigned not null,
	comment varchar(255) null,
	create_time timestamp default CURRENT_TIMESTAMP not null
);

create table tvm_service_to_uid_by_env
(
	service_id int(11) unsigned not null,
	uid bigint unsigned not null,
	comment varchar(255) null,
	environment enum('production', 'testing') not null,
	create_time timestamp default CURRENT_TIMESTAMP not null
);

create table tvm_services
(
	service_id int(11) unsigned not null,
	name varchar(255) not null,
	comment varchar(255) null,
	create_time timestamp default CURRENT_TIMESTAMP not null
);

create table tvm_services_by_env
(
	service_id int(11) unsigned not null,
	name varchar(255) not null,
	comment varchar(255) null,
	environment enum('production', 'testing') not null,
	create_time timestamp default CURRENT_TIMESTAMP not null,
	primary key (service_id, environment)
);

create table tvm_services_by_function_by_env
(
	`function` varchar(50) not null,
	service_id int(11) unsigned not null,
	comment varchar(255) null,
	environment enum('production', 'testing') not null,
	create_time timestamp default CURRENT_TIMESTAMP not null,
	primary key (`function`, service_id, environment)
);

create table ua_code_counters
(
	counter_id bigint null
);

create table user_comments
(
	counter_id int unsigned not null,
	user_id bigint unsigned not null,
	comment varchar(255) not null,
	update_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
	primary key (counter_id, user_id)
);

create table user_data_protection_regions
(
	id bigint unsigned auto_increment
		primary key,
	region_id bigint unsigned not null,
	status enum('active', 'deleted') default 'active' not null
);

create table user_options
(
	uid int unsigned not null
		primary key,
	max_delegates tinyint(4) unsigned not null,
	max_day_requests int unsigned null
);

create table if not exists goal_id_sequence
(
    goal_id bigint auto_increment primary key
);

create table user_params_uploadings
(
	uploading_id int(11) unsigned auto_increment
		primary key,
	counter_id int(11) unsigned not null,
	layer_id int(11) unsigned not null,
	uploader_id int(21) unsigned null,
	create_time timestamp default CURRENT_TIMESTAMP not null,
	content_id_type enum('user_id', 'client_id') null,
	action enum('update', 'delete_keys') not null,
	status enum('uploaded', 'confirmed', 'processed_partly', 'processed_fully', 'processing_failed', 'linkage_failure') default 'uploaded' not null,
	repository_chunk_id varchar(100) null,
	comment varchar(255) null,
	line_quantity int null,
	linked_quantity int null,
	linked_percentage varchar(10) null,
	failure_reason varchar(200) null,
	processed_line_quantity int default 0 not null,
	linked_time datetime null,
	processed_time datetime null
);

create table if not exists counters_delete_log
(
    log_id bigint unsigned auto_increment,
    counter_id int(11) unsigned not null,
    uid bigint unsigned,
    action enum('delete', 'undelete'),
    delete_time datetime,
    is_gdpr_delete tinyint(1),
    primary key (log_id)
);

create index `index`
	on user_params_uploadings (counter_id);

create index layer_id_status
	on user_params_uploadings (layer_id, status);

create index status
	on user_params_uploadings (status);

create table user_quota
(
	uid bigint default 0 not null
		primary key,
	multiplier double unsigned default '2' not null
);

CREATE TABLE gdpr_deleted_counters
(
    counter_id INT NOT NULL
        primary key,
    action_uid BIGINT NOT NULL,
    purge_time DATETIME NOT NULL,
    purged TINYINT(1) NOT NULL,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

create table wv2_counters
(
	counter_id int unsigned not null
		primary key,
	last_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP
);

create index last_time
	on wv2_counters (last_time);

create table wv_5percent
(
	counter_id int unsigned default 0 not null
);

create index counter_id
	on wv_5percent (counter_id);

create table wv_percent
(
	counter_id int unsigned default 0 not null
);

create index counter_id
	on wv_percent (counter_id);

create table yt_only_counters
(
	counter_id int unsigned not null
		primary key,
	add_time timestamp default CURRENT_TIMESTAMP not null
);

create view currency_last_rate_dates_view as select `conv_main`.`currency_rates`.`currency_code` AS `currency_code`,max(`conv_main`.`currency_rates`.`rate_date`) AS `last_rate_date` from `conv_main`.`currency_rates` group by `conv_main`.`currency_rates`.`currency_code`;

create view currency_rates_view as select `conv_main`.`currency_rates`.`currency_code` AS `currency_code`,`conv_main`.`currency_rates`.`from_usd_rate` AS `from_usd_rate`,cast(round((`conv_main`.`currency_rates`.`from_usd_rate` * 1000000),0) as unsigned) AS `from_usd_rate_in_micro`,cast(round((`conv_main`.`currency_rates`.`from_usd_rate` * 1000000),0) as unsigned) AS `from_usd_rate_in_micro_uint64`,`conv_main`.`currency_rates`.`rate_date` AS `rate_date` from `conv_main`.`currency_rates`;

create view currency_time_zones_view as select `all_rates`.`currency_code` AS `currency_code`,`tz`.`name` AS `time_zone` from `conv_main`.`currency_rates` `all_rates` join `conv_main`.`currency_last_rate_dates_view` `last_rates` join `conv_main`.`time_zones` `tz` where ((`all_rates`.`currency_code` = `last_rates`.`currency_code`) and (`tz`.`time_zone_id` = `all_rates`.`time_zone_id`)) group by `all_rates`.`currency_code`;

delimiter |
create procedure copy_site_path(IN num_to_process int)
BEGIN
DECLARE processed INT DEFAULT 0;
DECLARE max_counter INT DEFAULT 0;
DECLARE current INT DEFAULT 0;


SELECT MAX(counter_id) FROM counters INTO max_counter;

WHILE current < max_counter AND processed < num_to_process DO
  BEGIN
    DECLARE CONTINUE HANDLER FOR 1213 SELECT 'error';
    UPDATE conv_main.counters SET site_path = site, mirrors_paths = replace(mirrors, ',', '#') WHERE counter_id >= current AND counter_id < current + 1000 LIMIT 1000;
    SET processed = processed + ROW_COUNT();
    SET current = current + 1000;
    COMMIT;
  END;
END WHILE;
select 'end procedure';
END;
|

create procedure update_limit_to_null_limited(IN threshold int, IN num_to_process int)
BEGIN
DECLARE processed INT DEFAULT 0;
DECLARE max_counter INT DEFAULT 0;
DECLARE current INT DEFAULT 0;


SELECT MAX(counter_id) FROM counters INTO max_counter;

WHILE current < max_counter AND processed < num_to_process DO
  BEGIN
    DECLARE CONTINUE HANDLER FOR 1213 SELECT 'error';
    UPDATE conv_main.counters SET wv_visits_limit = NULL WHERE counter_id >= current AND counter_id < current + 1000 AND wv_visits_limit < threshold LIMIT 1000;
    SET processed = processed + ROW_COUNT();
    SET current = current + 1000;
    COMMIT;
  END;
END WHILE;
select 'end procedure';
END;
|

create procedure updatecounters(IN threshold int)
BEGIN
DECLARE processed INT DEFAULT 1;
DECLARE max_counter INT DEFAULT 0;
DECLARE current INT DEFAULT 0;
DECLARE CONTINUE HANDLER FOR 1213
SELECT 'error';

SELECT MAX(counter_id) FROM counters INTO max_counter;

WHILE current < max_counter DO
    UPDATE conv_main.counters SET wv_visits_limit = threshold WHERE counter_id >= current AND counter_id < current + 1000 AND wv_visits_limit < threshold LIMIT 1000;
    SET current = current + 1000;
    COMMIT;
END WHILE;
END;
|
