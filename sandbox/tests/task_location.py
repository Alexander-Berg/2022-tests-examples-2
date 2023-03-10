from __future__ import absolute_import

from sandbox import common


RTFM_URL = "https://wiki.yandex-team.ru/sandbox/quickstart/#code-structure"


def test__task_location(project_types):
    for task_type, task_location in project_types.iteritems():
        module_name = task_location.cls.__module__
        split_name = module_name.split(".")
        if common.system.inside_the_binary() and split_name[0] == "sandbox":
            split_name = split_name[1:]

        assert len(split_name) > 2 or task_type in _ALLOWED_TASK_TYPES, (
            "Task class of type {} is located in package {}. "
            "It's not allowed to place new task classes to top-level packages. "
            "Use your project's folder, please. Details here: {}".format(
                task_type, module_name, RTFM_URL
            )
        )


def _allowed_task_types():
    lines = []
    for task_type, task_location in common.projects_handler.load_project_types(force_from_fs=True).iteritems():
        module_name = task_location.cls.__module__
        if len(module_name.split(".")) <= 2:
            lines.append('    "{}",'.format(task_type))
    return "\n".join(sorted(lines))


# Please, do not add anything to this white list.
# Test is created in the sake of better code structure and its more convenient usage.
_ALLOWED_TASK_TYPES = {
    "ADDRS_SHARDED_BASESEARCH_PERFORMANCE",
    "ADDRS_TEST_BASESEARCH_PERFORMANCE",
    "ALLURE_REPORT_TASK",
    "ANALYZETHIS_IPREG",
    "ANNOTATE_CGI_PARAMS",
    "ANNOTATE_FML_2575_COMMENTS",
    "ANTIROBOT_COLLECT_FEATURES",
    "APP_PERFORMANCE_TEST",
    "APP_PERFORMANCE_TEST_BEST",
    "ARCADIA_PY_SCRIPT_RUNNER",
    "AUTOCHECK_CMAKELISTS_UNREACHABILITY",
    "AUTOCHECK_COMPARE_DEPENDENCIES",
    "AUTOCHECK_DIFF",
    "AUTOCHECK_DIR_GRAPH_TASK",
    "AUTOCHECK_DISMISSED_OWNERS",
    "AUTOCHECK_EMULATION_TASK",
    "AUTOCHECK_RESPONSIBILITY",
    "AUTOCHECK_STATISTICS_TASK",
    "AUTOCHECK_TESTS_STATISTICS",
    "BACKUP_MONGO",
    "BACKUP_MONGO_MANY_DATABASES",
    "BACKUP_NANNY_MONGODB",
    "BAKE_NEWS_RELEASER_DEPLOY_GRAPHS",
    "BATCH_WEB_RESULTS_CHECKER",
    "BB_VIEWER_UPDATE_BASES",
    "BEGEMOT_RUN_LIGHT_TESTS",
    "BEGEMOT_TEST_PERFORMANCE",
    "BLENDER_CHECK_REARR_SET",
    "BLENDER_CREATE_BACK_EXPERIMENT",
    "BLENDER_RD_TIMINGS_2_RAZLADKI",
    "BLENDER_REMOVE_EXPERIMENT",
    "BNO_APP_BUILD",
    "BNO_APP_HOST_TO_APP_BUILD",
    "BNO_NEWS_BUILD",
    "BNO_NEWS_HOSTS_BUILD",
    "BNO_RECIPES_BUILD",
    "BNO_UPLOAD_IMAGES",
    "BNO_UTILS_BUILD",
    "BROADMATCHING_TASK",
    "BROADMATCH_BUILD_MR_CATALOGIA",
    "BROADMATCH_OVERDRAFT",
    "BUILD_ABGAME_BACKEND",
    "BUILD_ABGAME_FRONTEND",
    "BUILD_ADDR_SNIPPET_DATA",
    "BUILD_ADDR_SNIPPET_DATA_REQUESTER",
    "BUILD_ALEMATE",
    "BUILD_APACHE_BUNDLE",
    "BUILD_ATOM_DAEMON",
    "BUILD_ATOM_PROMOLIB_PROXY_CONFIG",
    "BUILD_AURORA_BUNDLE",
    "BUILD_AVTOMATIKA",
    "BUILD_AVTOMATIKA_UI",
    "BUILD_AWACS",
    "BUILD_BALANCER_CONFIGS",
    "BUILD_BALANCER_CONFIG_GENERATOR",
    "BUILD_BALANCER_NANNY_TRAFFIC_CONTROL_DASHBOARDS",
    "BUILD_BASS",
    "BUILD_BASS_CI",
    "BUILD_BEGEMOT_EXECUTABLE",
    "BUILD_BEGEMOT_EXECUTABLE_2",
    "BUILD_BEGEMOT_LIGHT_TEST_CONFIG",
    "BUILD_BKHT_TICKERS_APP",
    "BUILD_BLENDER_LIBBLNDR",
    "BUILD_BLOCKSTAT_DICT",
    "BUILD_BREAKPAD",
    "BUILD_BSCONFIG",
    "BUILD_CACHE_DAEMON",
    "BUILD_CLANG",
    "BUILD_CLANG_FOR_ALL",
    "BUILD_CLICK_POOL",
    "BUILD_CLUSTERMASTER",
    "BUILD_CLUSTERMASTER_DEB",
    "BUILD_CLUSTERSTATE",
    "BUILD_CLUSTER_API",
    "BUILD_CMAKE",
    "BUILD_CMAKE_FOR_ALL",
    "BUILD_CONFIG_GENERATOR",
    "BUILD_CONFIG_GENERATOR_REPO",
    "BUILD_CONFIG_GENERATOR_SERVICE",
    "BUILD_CONVEYOR_DASHBOARD",
    "BUILD_CONVEYOR_DASHBOARD_BUSINESS_LOGIC",
    "BUILD_CONVEYOR_DASHBOARD_CACHER",
    "BUILD_CONVEYOR_DASHBOARD_FRONT",
    "BUILD_CONVEYOR_DASHBOARD_FRONT_PROXY",
    "BUILD_CONVEYOR_DASHBOARD_MK2",
    "BUILD_CONVEYOR_DASHBOARD_MK2_TEST",
    "BUILD_CORES_VIEW",
    "BUILD_COVERAGE",
    "BUILD_CUSTOM_NGINX",
    "BUILD_CVDUP_BUNDLE",
    "BUILD_CV_COLLAGE_DETECTOR",
    "BUILD_CY_HASH",
    "BUILD_DBMERGE_TOOL",
    "BUILD_DELAYED_VIEW_ENTITY_BASE_TRIE",
    "BUILD_DELAYED_VIEW_SERIAL_BASE_TRIE",
    "BUILD_DOCKER_IMAGE",
    "BUILD_DOCKER_IMAGE_FROM_GIT",
    "BUILD_DOCKER_IMAGE_V6",
    "BUILD_DOCKER_IMAGE_V6_01",
    "BUILD_DOCKER_IMAGE_V6_TEST_RESOURCE",
    "BUILD_DOLBILO_TOOLS",
    "BUILD_DYNAMIC_MODELS",
    "BUILD_ETCD",
    "BUILD_EXPCOOKIER",
    "BUILD_EXPERIMENTS_ADMINKA",
    "BUILD_EXPERIMENTS_ADMINKA_ENV",
    "BUILD_EXPERIMENTS_ADMINKA_GEO",
    "BUILD_EXPERIMENTS_ADMINKA_UTILS",
    "BUILD_EXPLOG_DAEMON",
    "BUILD_EXP_MR_SERVER",
    "BUILD_FAKE_RESOURCE",
    "BUILD_FAVICON_ROBOT",
    "BUILD_FILTER_TRIE",
    "BUILD_FIX_QUERIES",
    "BUILD_FLAME_GRAPH_BUNDLE",
    "BUILD_FML_PLOT",
    "BUILD_FML_POOL_STATS",
    "BUILD_FRESHNESS_SCRIPTS",
    "BUILD_GCC",
    "BUILD_GCC_FOR_ALL",
    "BUILD_GDB",
    "BUILD_GDB_FOR_ALL",
    "BUILD_GEMINI",
    "BUILD_GEOSEARCH",
    "BUILD_GEOSEARCH_TOOLS",
    "BUILD_GGS_CONFIG",
    "BUILD_GOLEM_DEB",
    "BUILD_GO_PACKAGE",
    "BUILD_GPERFTOOLS",
    "BUILD_GREENBOX_BUNDLE",
    "BUILD_HAPROXY",
    "BUILD_HG",
    "BUILD_HG_FOR_ALL",
    "BUILD_HIGHLANDER_DATA_FULL",
    "BUILD_HIGHLANDER_DATA_UPDATE",
    "BUILD_HTTP_GRIDFS",
    "BUILD_ICOOKIE_BLACKLIST",
    "BUILD_ICOOKIE_DAEMON",
    "BUILD_IDX_URL_DUPS",
    "BUILD_IMAGEPARSER_RAW",
    "BUILD_IMAGES_FACTORS_BUNDLE",
    "BUILD_IMAGES_FAST_MR_INDEX_BUNDLE",
    "BUILD_IMAGES_MR_INDEX_CONFIG_CHECKER",
    "BUILD_IMAGES_TAGS_BUNDLE",
    "BUILD_IMAGES_USERDB_BUNDLE",
    "BUILD_IMPROXY_BUNDLE",
    "BUILD_INFECTED_SERP_MASKS",
    "BUILD_INFRA_SHARDTOOL",
    "BUILD_INSTANCECTL_BINARY",
    "BUILD_INSTANCE_CTL",
    "BUILD_ISS_CACHER",
    "BUILD_ISS_CAPPER",
    "BUILD_ISS_SHARDS",
    "BUILD_ITS",
    "BUILD_JAVA_JDK",
    "BUILD_JUPITERTOOL",
    "BUILD_JUPITER_SHARD",
    "BUILD_KIWI_TRIGGERS",
    "BUILD_KOMUTATOR",
    "BUILD_KWMKTORRENT",
    "BUILD_KWMKTORRENT_FOR_ALL",
    "BUILD_KWMQBUILD",
    "BUILD_KWMQBUILD_FOR_ALL",
    "BUILD_KWRICH",
    "BUILD_LEMUR",
    "BUILD_LIBFFI",
    "BUILD_LIBMYSQLCLIENT",
    "BUILD_LIBOPENSSL",
    "BUILD_LIBSNAPPY",
    "BUILD_LIBSUPERRES",
    "BUILD_LICENSEPLATE",
    "BUILD_LOADLOGDUMP",
    "BUILD_MAPREDUCELIB_PY",
    "BUILD_MAPS_COMPANIES_POI_AND_URLS",
    "BUILD_MAPS_DATABASE_ADVERT",
    "BUILD_MAPS_DATABASE_POI",
    "BUILD_MAPS_FILTERED_HOST_FACTORS",
    "BUILD_MAPS_FILTERED_WEB_USER_FACTORS",
    "BUILD_MAPS_GEO_STATIC_FACTORS",
    "BUILD_MAPS_STATIC_FACTORS_DOWNLOADER",
    "BUILD_MAPS_WEB_INDEXANN",
    "BUILD_MARKET_BUKER_BIN",
    "BUILD_MARKET_CATALOGER_BIN",
    "BUILD_MARKET_GURU_BIN",
    "BUILD_MARKET_REPORT",
    "BUILD_MATRIXNET",
    "BUILD_MEDIAPORTRAITS_FRONTEND",
    "BUILD_MEMCACHED",
    "BUILD_MIDDLESEARCH_GEO_DATA_BUNDLE",
    "BUILD_MIKEY",
    "BUILD_MIRROR_SCHEDULER",
    "BUILD_MN_CUDA",
    "BUILD_MONGO",
    "BUILD_MONGO_TOOLS_PACKAGE",
    "BUILD_MONSYS_DC",
    "BUILD_MONSYS_DC_WITH_VENV",
    "BUILD_MONSYS_PROXY",
    "BUILD_MR_PACKET_LIB",
    "BUILD_MR_URLS_SHARDS",
    "BUILD_MUSCA",
    "BUILD_MX_OPS",
    "BUILD_MYSQLSERVER",
    "BUILD_NANNY",
    "BUILD_NANNY_DEB",
    "BUILD_NEHC",
    "BUILD_NEWS",
    "BUILD_NEWSD_EVLOGDUMP_EXECUTABLE",
    "BUILD_NEWSD_STATEWORK",
    "BUILD_NEWS_APACHECTL_SERVICE_CONFIG_BUNDLE",
    "BUILD_NEWS_APPHOST_DUMPERD",
    "BUILD_NEWS_APPHOST_DUMPERD_SERVICE_CONFIG_BUNDLE",
    "BUILD_NEWS_APPHOST_QUOTES",
    "BUILD_NEWS_APPHOST_QUOTES_SERVICE_CONFIG_BUNDLE",
    "BUILD_NEWS_APPHOST_ROUTERD",
    "BUILD_NEWS_APPHOST_ROUTERD_SERVICE_CONFIG_BUNDLE",
    "BUILD_NEWS_ARCHARDS_EXECUTABLE",
    "BUILD_NEWS_ARCHIVE_SHARD",
    "BUILD_NEWS_BAD_YANDEXUIDS",
    "BUILD_NEWS_GEN_MONGO_CONF",
    "BUILD_NEWS_GEN_ZK_CONF",
    "BUILD_NEWS_L_COOKIE_KEYS",
    "BUILD_NEWS_MEMCACHED",
    "BUILD_NEWS_MR_INDEXER",
    "BUILD_NEWS_NGINX",
    "BUILD_NEWS_NGINX_CONFIG_GENERATOR_EXECUTABLE",
    "BUILD_NEWS_NGINX_SERVICE_CONFIG_BUNDLE",
    "BUILD_NEWS_PACKAGE",
    "BUILD_NEWS_PYTHON3",
    "BUILD_NEWS_REDIS_SERVER",
    "BUILD_NEWS_RELEASER",
    "BUILD_NEWS_RELEASER_SERVICE_CONFIG_BUNDLE",
    "BUILD_NEWS_REPORT_CORE",
    "BUILD_NEWS_RKN_VIEWER",
    "BUILD_NEWS_SEARCH_SHARD",
    "BUILD_NEWS_SEARCH_SHARDS",
    "BUILD_NEWS_SEARCH_SHARD_BUILDER",
    "BUILD_NEWS_SLAVE_NEWSD_SERVICE_CONFIG_BUNDLE",
    "BUILD_NEWS_UATRAITS_BROWSER_XML",
    "BUILD_NEWS_UPPER_SERVICE_CONFIG_BUNDLE",
    "BUILD_NGINX",
    "BUILD_NGINX_CPLB",
    "BUILD_NINJA",
    "BUILD_NINJA_FOR_ALL",
    "BUILD_NISHOOTER",
    "BUILD_NISHOOTER_FRONT",
    "BUILD_NNINDEXER",
    "BUILD_NN_APPLIER",
    "BUILD_OCR",
    "BUILD_ONOTOLE",
    "BUILD_ONOTOLE3",
    "BUILD_ONTODB_API",
    "BUILD_ONTODB_CLARINET",
    "BUILD_ONTODB_FIXES_2_VIEWER",
    "BUILD_ONTODB_FIXES_STICKY",
    "BUILD_ONTODB_FIXES_VIEWER",
    "BUILD_ONTODB_ROBOT",
    "BUILD_ONTODB_RUNTIME",
    "BUILD_OPENSSL_EXECUTABLE",
    "BUILD_PACKAGES_FOR_REM",
    "BUILD_PACKAGE_AND_PORTO_LAYER",
    "BUILD_PEOPLESEARCH_TOOLS",
    "BUILD_PERCONA_XTRABACKUP",
    "BUILD_PERCONA_XTRADB_CLUSTER",
    "BUILD_PERS_TOOLS",
    "BUILD_POOL_MERGE_FILTER",
    "BUILD_POOL_SAMPLER",
    "BUILD_POOL_URLS_HELPER",
    "BUILD_PROJECT_STUB_NODEJS_PACKAGE",
    "BUILD_PRS_INTERSECTOR",
    "BUILD_PRS_UNRATER",
    "BUILD_PUMPKIN_INDEX",
    "BUILD_PUMPKIN_RESINFOD_BUNDLE",
    "BUILD_PYTHON_BUNDLE",
    "BUILD_PYTHON_BUNDLE2",
    "BUILD_PYTHON_DEV",
    "BUILD_QLOUD_INIT",
    "BUILD_QURL_RATES",
    "BUILD_RANKING_MIDDLE_VIDEOSEARCH",
    "BUILD_RATELIMITER",
    "BUILD_RAZLADKI",
    "BUILD_REACT_UI",
    "BUILD_READAHEAD",
    "BUILD_REARRANGE",
    "BUILD_REARRANGE_DYNAMIC",
    "BUILD_REDIS",
    "BUILD_REM_CLIENT",
    "BUILD_REPLICAMAP",
    "BUILD_REPLICAMAP2",
    "BUILD_REPLICAMAP3",
    "BUILD_REPLICAMAPC1R1",
    "BUILD_REPLICAMAPTEST",
    "BUILD_REPORT",
    "BUILD_REPORT_CORE",
    "BUILD_RESTORE_UNIMPL",
    "BUILD_ROBOT_PACKAGES",
    "BUILD_ROTOR",
    "BUILD_ROTOR_WL",
    "BUILD_ROTOR_WL_BUILDER",
    "BUILD_RTLINE",
    "BUILD_RTLINE_CONFIG",
    "BUILD_RTYSERVER",
    "BUILD_RTYSERVER_CONFIG",
    "BUILD_RTYSERVER_MAPS_USER_IF",
    "BUILD_RTYSERVER_MODELS",
    "BUILD_RTYSERVER_UTILS",
    "BUILD_SALMON",
    "BUILD_SEARCH",
    "BUILD_SEMANTIC_MF_VERIFIER",
    "BUILD_SEMANTIC_PUBLIC_API",
    "BUILD_SEMANTIC_YT_MAPPER",
    "BUILD_SENTRY_NGINX",
    "BUILD_SENTRY_VIRTUALENV",
    "BUILD_SEPELIB",
    "BUILD_SERVICE_TEMPLATE",
    "BUILD_SHARDMAP",
    "BUILD_SHARDTOOL",
    "BUILD_SHARDTOOL_EMPTY_INSTALL_SCRIPT",
    "BUILD_SHARD_TO_SSD",
    "BUILD_SHARP_EYE",
    "BUILD_SITESEARCH_CATALOG_INDEXER",
    "BUILD_SITESEARCH_MANAGER",
    "BUILD_SITESEARCH_PERIODIC",
    "BUILD_SITESEARCH_SEARCHAPI",
    "BUILD_SITESEARCH_SEARCHER",
    "BUILD_SITESEARCH_SUGGEST",
    "BUILD_SITESEARCH_SUPPORT",
    "BUILD_SITESEARCH_VIEWER",
    "BUILD_SITE_SUGGEST",
    "BUILD_SLAVE_NEWSD_APPHOST_REQUESTER",
    "BUILD_SNOWDEN_ARCHIVE",
    "BUILD_SPACETAGS_RAW",
    "BUILD_SPECSEARCH_PERL_BUNDLE",
    "BUILD_SPLIT_POOL",
    "BUILD_SPLIT_PROTO_POOL",
    "BUILD_SPORT_BASESEARCH",
    "BUILD_SPORT_PROXY_DATA",
    "BUILD_SPORT_PUSH_API",
    "BUILD_STATBOX_PUSHCLIENT",
    "BUILD_STATBOX_PUSHCLIENT_OLD",
    "BUILD_STATS_NANNY_SERVICES",
    "BUILD_SUGGEST_DEB",
    "BUILD_SUGGEST_FOR_ALL",
    "BUILD_SVN",
    "BUILD_SVN_FOR_ALL",
    "BUILD_SWITCH_ADMINKA",
    "BUILD_TEMPLATER",
    "BUILD_TEST_REQUESTS",
    "BUILD_TIMELINE",
    "BUILD_TMUX",
    "BUILD_TMUX_FOR_ALL",
    "BUILD_TSNET2",
    "BUILD_UKROP",
    "BUILD_UKROP_EXT",
    "BUILD_UKROP_TESTS",
    "BUILD_USERDATA_BETA_DUMP_DATA",
    "BUILD_UZOR",
    "BUILD_VALGRIND",
    "BUILD_VALGRIND_FOR_ALL",
    "BUILD_VIDEOSEARCH_BUNDLE",
    "BUILD_VIDEO_POPULAR_CONFIG",
    "BUILD_VIRTUALENV",
    "BUILD_WHITEHILL",
    "BUILD_WINE",
    "BUILD_WIZARD",
    "BUILD_WIZARD_CONFIG",
    "BUILD_WIZARD_EXECUTABLE",
    "BUILD_WIZARD_PROXY",
    "BUILD_YABS_YTSTAT",
    "BUILD_YABS_YTSTAT_COLLECTOR",
    "BUILD_YABS_YTSTAT_SUPERVISOR",
    "BUILD_YADI_TOOL",
    "BUILD_YASAP_HOT_FRONTEND",
    "BUILD_YASAP_ISEG",
    "BUILD_YASAP_TEST_PY_PACKAGE",
    "BUILD_YASM_BALANCER_REPORT",
    "BUILD_YDL",
    "BUILD_YMAKE",
    "BUILD_YOBJECT",
    "BUILD_ZOOKEEPER",
    "BUILD_ZOOLOCK",
    "BUILD_ZOOREST",
    "BUILD_ZOOTOPIA_PROJECT",
    "CALCULATE_MATRIXNET_MODELS_AND_PREDICTIONS",
    "CALCULATE_MATRIXNET_MODEL_AND_PREDICTIONS",
    "CALCULATE_MATRIXNET_PREDICTIONS_MEAN",
    "CALC_BUSINESS_RATING",
    "CALC_COVERAGE",
    "CALC_MAIN_RUBRIC",
    "CALC_PUSH_METRICS",
    "CALC_SIMILAR_ORGS",
    "CALC_SIMILAR_ORGS_HYPOTHESES",
    "CALC_SIMILAR_ORGS_PREPARATION",
    "CHECK_BEGEMOT_DEPENDENCIES",
    "CHECK_CACHEHIT_FOR_BETA",
    "CHECK_DOCKER_LXC",
    "CHECK_FRESH_DOCUMENTS",
    "CHECK_MATRIXNET_PREDICTIONS_DIFF",
    "CHECK_PORTS",
    "CHECK_RAZLADKA_PARSELIB",
    "CHECK_UNUSED_FACTORS",
    "CLEANUP_YT_DIRECTORY",
    "CLEAN_UP_BAD_PSI_CONTAINERS",
    "CLICKDAEMON_KEYGEN",
    "COCAINE_LAYERS_EXPORT_TO_REGISTRY",
    "COLLECT_ANTIROBOT_DATA",
    "COLLECT_RESOURCES",
    "COLLECT_TOP_QUERIES",
    "COMBINE_MR_TABLES",
    "COMPARE_APPHOST_SERVICE_RESPONSES",
    "COMPARE_BINARY_RESPONSES",
    "COMPARE_DBG_DOLBILKA_OUTPUTS",
    "COMPARE_DEPENDENCIES",
    "COMPARE_DIFF_TEST_EXAMPLE_OUTPUTS",
    "COMPARE_DYNAMIC_MODELS",
    "COMPARE_ESTFEATURES_OUTPUTS",
    "COMPARE_EVENTLOG_STATS",
    "COMPARE_FLAME_GRAPHS",
    "COMPARE_FUSION_RESPONSES",
    "COMPARE_GEOSEARCH_OUTPUTS",
    "COMPARE_GEOSEARCH_REQANS_LOGS",
    "COMPARE_GEOSEARCH_RESPONSES",
    "COMPARE_IDX_QUERY_OUTPUTS",
    "COMPARE_LOADLOGS",
    "COMPARE_MATRIXNETS",
    "COMPARE_METASEARCH_SUBSOURCE_REQUESTS",
    "COMPARE_MR_PROTO_POOLS",
    "COMPARE_MR_TABLES",
    "COMPARE_NEWSD_APPHOST_RESPONSES",
    "COMPARE_NEWSD_RESPONSES",
    "COMPARE_NEWS_BASESEARCH_RESPONSES",
    "COMPARE_PROD_AND_RSYA_RESPS",
    "COMPARE_PROFILE_STATS",
    "COMPARE_PROTO_POOLS",
    "COMPARE_PROXY_WIZARD_RESPONSES",
    "COMPARE_QLOSS_OUTPUTS",
    "COMPARE_ROUTERD_RESPONSES",
    "COMPARE_THUMB_DAEMON_RESPONSES",
    "COMPARE_UNISTAT",
    "COMPARE_YMAKE_DUMP",
    "COMPUTE_OFFLINE_METRICS_ONLINE_LEARNING",
    "CONVERT_VIDEO",
    "COPY_DATA_RUNTIME",
    "COUNT_UNKWNOWN_TASKS",
    "CREATE_CLUSTERSTATE_VENV",
    "CREATE_CROSS_MSVC_TOOLKIT",
    "CREATE_FUSION_DB",
    "CREATE_JAVA_JDK",
    "CREATE_LINUX_PACKAGE",
    "CREATE_PACKAGE",
    "CREATE_SHARDMAP_RESOURCE",
    "CREATE_TEXT_RESOURCE",
    "CREATE_UKROP_BRANCH",
    "CREATE_VENV",
    "DELETE_OLD_RESOURCES",
    "DELETE_OLD_RESOURCES_GEO",
    "DEPLOY_KIKIMR",
    "DEPLOY_NANNY_DASHBOARD",
    "DEPLOY_NANNY_DASHBOARD_DEV",
    "DEPLOY_NANNY_RELEASE_REQUESTS",
    "DEPLOY_NANNY_SHARDMAP",
    "DEPLOY_REFRESH_FROZEN",
    "DEPLOY_RESOURCES_TO_NANNY",
    "DEPLOY_UKROP",
    "DEPLOY_VIDEO_BASE_NEWDB_SHARDMAP",
    "DEPLOY_VIDEO_MMETA_SHARDMAP",
    "DEPLOY_WMCURLS_CACHE",
    "DRAW_FRESHNESS_PLOTS",
    "DUMP_AND_CALC_EVENTLOG",
    "DUMP_EVENTLOG",
    "DUMP_EVENTLOG_SINGLE_HOST",
    "ENTITYSEARCH_APPHOST_RESPONSES",
    "ENTITYSEARCH_BINARIES_BUILD",
    "ENTITYSEARCH_BRAVE_NEW_WORLD",
    "ENTITYSEARCH_COMPARE_APPHOST_RESPONSES",
    "ENTITYSEARCH_CONFIG_BUILD",
    "ENTITYSEARCH_CONVERT_DB",
    "ENTITYSEARCH_DATA_BUILD",
    "ENTITYSEARCH_LOGS",
    "ENTITYSEARCH_NMETA_REQS_TO_APPHOST_REQS",
    "ENTITYSEARCH_REALTIME_GENERATION",
    "ENTITYSEARCH_REALTIME_RELEASE",
    "ENTITYSEARCH_SHARP_SHOOTER",
    "ENTITYSEARCH_SHOOTER",
    "ENTITYSEARCH_UPDATE_CMAKE_RESOURCES",
    "ERF_MONITOR",
    "EXPERIMENTS_CONFIG_CHECK",
    "EXPERIMENTS_CONFIG_UPDATE",
    "EXPORT_GENCFG_TO_CAUTH",
    "EXTRACT_PANTHER_GUTS",
    "FAKE_BUILD_ROBOT_PACKAGES",
    "FAST_BASESEARCH_ACCEPTANCE",
    "FILTER_EVENTLOG",
    "FIND_URL_RELEASE",
    "FORMING_WEEKLY_REPORT",
    "FUZZ_YA_MAKE_TASK",
    "GENERATE_ALL_PLANS",
    "GENERATE_BALANCER_ACTIVE_CHECKS",
    "GENERATE_GENCFG_CLICKHOUSE_TABLES",
    "GENERATE_LINEAR_MODEL_BINARY_DUMP",
    "GENERATE_LINEAR_MODEL_BINARY_DUMP_LAUNCHER",
    "GENERATE_LINEAR_MODEL_SHARDING_BASE",
    "GENERATE_OCSP_RESPONSE_FILES",
    "GENERATE_PLAN_FROM_QUERIES",
    "GENERATE_SLOW_PLAN",
    "GENERATE_SPORT_DEVICE_IDS",
    "GENERATE_THUMB_DAEMON_REQUESTS",
    "GENERATE_USERS_QUERIES",
    "GEN_CHAIN_ADVERTS",
    "GEN_NEWS_REPORT_DATA",
    "GET_ADVQUICK_DATABASE",
    "GET_ARCNEWS_SHARDMAP",
    "GET_FML_CONVEYOR_AUTOFORMULAS_SNAPSHOT",
    "GET_FORMULA_CONVEYORS_LIST",
    "GET_FUSION_MIDDLESEARCH_RESPONSES",
    "GET_FUSION_PROD_CONFIGS",
    "GET_FUSION_RESPONSES",
    "GET_GEOMETASEARCH_RESPONSES",
    "GET_HAMSTER_APPHOST_RESPONSES",
    "GET_HYPER_CAT_ID",
    "GET_IMAGES_MR_INDEX_CONFIG",
    "GET_IMAGES_QUICK_THUMB_SHARDMAP",
    "GET_IMAGES_RATED_URLS",
    "GET_LEMUR_VINTAGE_MAP_TEST_DATA",
    "GET_MAPS_SEARCH_BUSINESS_RESPONSES",
    "GET_MEDIA_SHARDMAP_FROM_SVN",
    "GET_MMETA_AND_INT_RESPONSES",
    "GET_MMETA_RESPONSES",
    "GET_NEWSD_APPHOST_RESPONSES",
    "GET_NEWSD_RESPONSES",
    "GET_PARTNER_MONEY_TOP_FOR_ANALYTICS",
    "GET_POKAZOMETER_DATABASE",
    "GET_PROXY_WIZARD_RESPONSES",
    "GET_QUERIES_FROM_EVENTLOG",
    "GET_QUERIES_FROM_PLAN",
    "GET_RANDOM_PERSONAL_UIDS",
    "GET_RANDOM_REQUESTS",
    "GET_REFRESH_INDEX_FOR_TEST",
    "GET_ROUTERD_RESPONSES",
    "GET_THUMB_DAEMON_RESPONSES",
    "GET_VIDEO_MIDDLESEARCH_DATABASE",
    "GET_VIDEO_QUICK_SEARCH_DATABASE",
    "GET_VIDEO_SEARCH_DATABASE",
    "GET_WIZARD_PRINTWZRD_RESPONSES",
    "GET_WIZARD_PROD_QUERIES",
    "GET_WIZARD_RESPONSES",
    "GLYCINE",
    "HELLO_PRIME_TASK",
    "HWCARDS_PUSH",
    "IEX_BUILD_BINS",
    "IEX_BUILD_GRAMMARS",
    "IEX_BUILD_PACKAGES",
    "IEX_COMPARE_FUNC_TEST_RESULTS",
    "IEX_GET_LAST_RESULTS",
    "IEX_IMPORT_PATTERNS",
    "IEX_PREPARE_RELEASE",
    "IEX_RELEASE",
    "IEX_TESTS_MANAGER",
    "IEX_TEST_FUNC",
    "IEX_UPDATE_CONTENTLINE_MODEL",
    "IMPROXY_GENERATE_REQUESTS",
    "IMPROXY_GET_PROD_RESPONSES",
    "IMPROXY_GET_RESPONSES",
    "IMPROXY_SET_BASE_VERSION",
    "IMPROXY_TEST_FUNC",
    "IMPROXY_TEST_PERFORMANCE",
    "INSTALL_VIDEO_QUOTES_TASK",
    "ISS_CRUTCH",
    "ITS_SET_VALUE",
    "KIMKIM_TEST",
    "LAUNCH_RUNTIME_CLOUD_BALANCER_TASKS",
    "LB_CHECK_SAAS_CONSISTENCY",
    "LB_EXTRACT_SHARD",
    "LB_GET_SAAS_RESPONSES",
    "LOAD_MARKET_REPORT_INDEX",
    "MAKE_ARCHIVE_NEWSD_SHARD",
    "MAKE_CONVEYOR_FML_PROCESS_TEMPLATES_LIST_REPORT",
    "MAKE_ESTIMATED_POOL",
    "MAKE_FML_CONVEYOR_FORMULA_COMMIT_REPORT",
    "MAKE_GEODB_DATA",
    "MAKE_GEODB_DATA_2",
    "MAKE_GEODB_DATA_FROM_REVISION",
    "MAKE_IDX_OPS_POOL",
    "MAKE_MAPS_PACKAGES_LIST",
    "MAKE_NEW_PERSONAL_RESOURCE",
    "MAKE_NEW_PERSONAL_RESOURCE_SUBTASK",
    "MAKE_NIRVANA_WORKFLOW_SNAPSHOT",
    "MAKE_PERSONAL_BUNDLE",
    "MAKE_SHARD",
    "MAKE_TRAIN_MATRIXNET_ON_CPU_NIRVANA_OPS",
    "MAPS_DATABASE_BUSINESS_QUALITY_ACCEPTANCE",
    "MARKDOWN_TO_PDF",
    "MARKET_BUKER_SHOOTER",
    "MARKET_CATALOGER_SHOOTER",
    "MARKET_DO_SOME_TEST",
    "MARKET_GURU_SHOOTER",
    "MARKET_WIZARD_TIRES",
    "MARK_CURRENT_PROD_RESOURCES",
    "MEDIA_COPY_SANDBOX_RESOURCE",
    "MEDIA_FETCH_OCSP_RESPONSE",
    "MEDIA_SHARDMAP_BY_SVN",
    "MEDIA_TASK_MONITORING",
    "MEDIA_TEST_COMMERCIAL_BALANCER",
    "MISCDATA_PREP_UPDATE",
    "MIX_QUERIES_EXPERIMENTS_REGIONS",
    "ML_ENGINE_DUMP_MONITOR",
    "MMETA_FREQUENT_STABILITY",
    "MODEL_DATE_MONITOR",
    "MODIFY_RESOURCE",
    "MOLLY_RUN",
    "MULTIMEDIA_RTMR_MONITOR",
    "NANNY_BUILD_BASE",
    "NANNY_DELETE_SNAPSHOT_RESOURCE",
    "NANNY_REMOTE_COPY_RESOURCE",
    "NEWS_AUTORELEASABLE_TASK",
    "NEWS_UNPACK_GEODATA_TZ_DATA",
    "OCR_API_LOGS",
    "OCR_BUILD",
    "OCR_BUILD_TEST",
    "ONLINE_LEARNING_DUMP_TXT_PREPARE",
    "ORG1_AGGR_DATA_BUILDER",
    "ORG1_SERP_DOWNLOADER",
    "PANTERA_FACTORS",
    "PARALLEL_DUMP_EVENTLOG",
    "PATCH_NEWS_APP_HOST_GRAPHS",
    "PATCH_PLAN",
    "PATCH_QUERIES",
    "PREPARE_QUERIES_AND_BINARIES_FOR_REARRANGE_DYNAMIC_TESTS",
    "PRIEMKA_VIDEO_BASESEARCH_DATABASE",
    "PROCESS_SIMILARS_PREPARAT",
    "PROGRAM_CRASHER",
    "PROXY_WIZARD_WEATHER_TRANSLATIONS",
    "PUBLISH_NEWS_ARCHIVE",
    "PUBLISH_NEWS_ARCHIVE_WRAPPER",
    "PUBLISH_SIMILAR_ORGS",
    "PUSH_BUILD",
    "PUSH_BUILD_CI",
    "RELEASE_ANTIROBOT_DATA",
    "RELEASE_ANTIROBOT_FORMULAS",
    "RELEASE_ANY",
    "RELEASE_ARCNEWS_SHARDMAP",
    "RELEASE_BALANCER_CONFIG_GENERATOR",
    "RELEASE_CONFIG_GENERATOR",
    "RELEASE_CONFIG_GENERATOR_SERVICE",
    "RELEASE_CYCOUNTER_FILES",
    "RELEASE_DELAYED_VIEW_TRIES",
    "RELEASE_DOMAIN_HAS_METRIKA_TRIE",
    "RELEASE_G2LD_LIST",
    "RELEASE_ISS_PRESTABLE",
    "RELEASE_MEDIA_SHARDMAPS",
    "RELEASE_NANNY_SHARDMAP",
    "RELEASE_PARENT_TASK",
    "RELEASE_PERSONAL_BUNDLE",
    "RELEASE_POETRYLOVER_SHARDMAP",
    "RELEASE_QUICK_REARRANGE_DATA",
    "RELEASE_REPORT_DATA_RUNTIME_BUNDLE",
    "RELEASE_REPORT_DATA_RUNTIME_BUNDLE2",
    "RELEASE_SDCH_DICTIONARY_PACK",
    "RELEASE_SHARD_INSTALL_SCRIPTS",
    "RELEASE_SMISEARCH_SHARD",
    "RELEASE_SPORT_PROXY_DATA",
    "RELEASE_TASK",
    "RELEASE_VIDEO_VEGAS_CONFIG",
    "RELEASE_YT_LOCAL",
    "RELEV_FML_UNUSED",
    "REMOVE_REARRANGE_DYNAMIC_FORMULAS",
    "REPORT_CHECK_AUTOTEST_STATUS",
    "REPORT_DATA_RUNTIME",
    "REPORT_DATA_RUNTIME_ITEM",
    "REPORT_DATA_RUNTIME_LAST_TAG",
    "REPORT_DATA_RUNTIME_RT",
    "REPORT_DATA_RUNTIME_TAGS",
    "REPORT_RULE_TEST_FULL",
    "RESHARE_SHARDS",
    "RESHARE_SHARDS_ON_HOST",
    "RESOURCES_TO_YT",
    "RESOURCE_LOADER_FROM_NANNY",
    "RESTORE_INDEXFRQ",
    "RESTORE_MONGO",
    "RUN_CUBE_STATUS",
    "RUN_DISK_PYTHON_SCRIPT",
    "RUN_IDX_OPS",
    "RUN_IDX_OPS_EST_FEATURES",
    "RUN_IDX_OPS_URLNORM_TEST",
    "RUN_NANNY_DASHBOARD_RECIPE",
    "RUN_NANNY_RECIPE",
    "RUN_NEWS_ARCHIVE_CLUSTERING",
    "RUN_NEWS_LOADTEST",
    "RUN_NIRVANA_BASED_INTEGRATION_TEST",
    "RUN_NIRVANA_ONLINE_GRAPH_LAUNCHER",
    "RUN_NIRVANA_ONLINE_LEARNING",
    "RUN_NIRVANA_WORKFLOW",
    "RUN_PRINTWZRD",
    "RUN_PYTHON_FROM_WHEEL",
    "RUN_PYTHON_SCRIPT",
    "RUN_REFRESH_ACCEPTANCE",
    "RUN_REM_JOBPACKET",
    "RUN_REM_JOBPACKET_SLIM",
    "RUN_SCRIPT",
    "RUN_SPYNET_YTRANK",
    "RUN_UPDATE_WIKIPEDIA",
    "RUN_VIDEO_QUOTES_TASK",
    "RUN_YABS_PYTHON_SCRIPT",
    "RUN_YQL",
    "SAAS_ALERTS_MANAGE",
    "SAAS_GARDEN_GRAPH_CONVERT",
    "SAAS_GARDEN_HELPER",
    "SAAS_KV_UPLOADER",
    "SAAS_ROADS_GRAPH_MATCHER",
    "SAAS_ROADS_GRAPH_TRAFFIC_HISTORY_BUILDER",
    "SAMOGON_TEST_PACKAGE",
    "SAMPLE_MISCDATA_SOURCES",
    "SAMPLE_USERDATA_FAST_SESSIONS",
    "SAMPLE_USER_BROWSE_SESSIONS",
    "SAMPLE_USER_COUNTERS_SESSIONS",
    "SAMPLE_USER_SEARCH_SESSIONS",
    "SANITIZER_BUILD",
    "SANITIZER_COMPARE_FUNC_TEST_RESULTS",
    "SANITIZER_TEST_FUNC",
    "SEARCH_CREATE_SHARDMAP",
    "SERP_COLLECTOR",
    "SHOOT_LOG_PREPARE",
    "SHOOT_METASEARCH_WITH_PLAN",
    "SIMILAR_ORGS_DO_ALL",
    "SPAWN_TEST_CONFIG_GENERATOR",
    "STABILIZE_NEWS_APACHE_BUNDLE",
    "STABILIZE_NEWS_APP_HOST_BUNDLE",
    "STABILIZE_NEWS_APP_HOST_PRODUCTION_INSTANCECTL_CONF",
    "STABILIZE_NEWS_APP_HOST_SRC_SETUP_BUNDLE",
    "STABILIZE_NEWS_APP_HOST_SRC_SETUP_PRODUCTION_LOOP_CONF",
    "ST_TASK_OOPS_100",
    "SUGGEST_TEST_SECOND",
    "SUP_BACKUP_COMBINE",
    "SUP_REGISTRATION_LOAD",
    "SUP_UPDATE_APP_TAGS",
    "SUP_UPDATE_GEO_TAGS",
    "SUSPICIOUS_COMMITS",
    "SWITCH_VIDEO_DATABASE",
    "SWITCH_VIDEO_DATABASE_NG",
    "SWITCH_VIDEO_EXPERIMENTAL_DATABASE_NG",
    "SYNC_ICEBERG_TASK",
    "TEAMCITY_RUNNER",
    "TEAMCITY_RUNNER_PIP",
    "TEST_ALEMATE",
    "TEST_AURORA_BUNDLE",
    "TEST_BALANCER_FUNC",
    "TEST_CONFIG_GENERATOR",
    "TEST_CONFIG_GENERATOR_SERVICE_TRAVERSE",
    "TEST_CVDUP_ON_SYNTHETIC",
    "TEST_DYNAMIC_MODELS_ARCHIVE",
    "TEST_DYNAMIC_MODELS_FEATURES",
    "TEST_EXECUTE_WITH_PGO_TASK",
    "TEST_FIND_URL_BUCKET",
    "TEST_FROM_EXTERNAL_SCRIPT",
    "TEST_FRONT_METRICS_LOGS",
    "TEST_FUSION_PERFORMANCE",
    "TEST_FUSION_PERFORMANCE_BEST",
    "TEST_INFO_REQUESTS",
    "TEST_INSTANCE_CTL",
    "TEST_INSTANCE_RESOLVER",
    "TEST_LEMUR_VINTAGE",
    "TEST_LEMUR_VINTAGE_COMPARE",
    "TEST_MAPS_SEARCH_BUSINESS_PERFORMANCE",
    "TEST_MARKET_REPORT_MONEY",
    "TEST_MARKET_REPORT_PERFORMANCE",
    "TEST_MATRIXNET",
    "TEST_MIDDLESEARCH_SINGLE_HOST_FUSION",
    "TEST_NEH",
    "TEST_NEWSD_PERFORMANCE",
    "TEST_OCR_RUNNER",
    "TEST_PEOPLESEARCH_PYLIB",
    "TEST_PEOPLESEARCH_TOOL",
    "TEST_PEOPLESS",
    "TEST_PROXY_WIZARDS_REQUESTS",
    "TEST_QUICK_PERFORMANCE",
    "TEST_REFRESH_PERFORMANCE_BEST",
    "TEST_REPORT_CONTEXT",
    "TEST_REPORT_PERFORMANCE",
    "TEST_REPORT_UNIT",
    "TEST_REPORT_UNIT_COVERAGE",
    "TEST_REPORT_UNIT_COVERAGE_BY_COMMIT",
    "TEST_REPORT_UNIT_UPDATE_RES",
    "TEST_ROUTERD_PERFORMANCE",
    "TEST_RTYSERVER_DOLBILOM",
    "TEST_RTYSERVER_MANAGE",
    "TEST_RTYSERVER_MULTI",
    "TEST_RTYSERVER_PROXY",
    "TEST_RTYSERVER_UNIT",
    "TEST_RTYSERVER_UT",
    "TEST_SAAS_FML_UT",
    "TEST_SITA_UNIT",
    "TEST_SUPERMIND",
    "TEST_SYNC_RESOURCE",
    "TEST_THUMB_DAEMON",
    "TEST_THUMB_DAEMON_FUNC",
    "TEST_TRAIN_MATRIXNET_ON_CPU",
    "TEST_TRANSPARENT_HUGEPAGES",
    "TEST_UT_MEMCHECK",
    "TEST_WITH_VALGRIND",
    "TEST_WIZARD_PERFORMANCE_BEST",
    "THUMBS_BAN_BUILD_QUERYSEARCH",
    "TMP_ABT_METRICS_DEV",
    "TOOLS_CAAS_CONFIGURE",
    "TOOLS_CAAS_GENCONFIG",
    "TOP_MUSICIANS_FROM_PPB_POSTLOG",
    "TOUCH_BUILD_PUMPKIN_SERP",
    "TOUCH_TEST_PUMPKIN_SERP",
    "TV_SNIP_DATA_BUILD",
    "TV_SNIP_DATA_BUILD_GMAKE",
    "TV_SNIP_DATA_RELEASE",
    "UNPACK_RESOURCES_ARCHIVE",
    "UPDATE_ABUSE_REMODERATION_TABLE",
    "UPDATE_BUSINESS_COMPUTED_RATING",
    "UPDATE_BUSINESS_DETAILED_RATINGS",
    "UPDATE_BUSINESS_PHOTOS",
    "UPDATE_BUSINESS_RATINGS",
    "UPDATE_BUSINESS_SNIPPET_PHOTOS",
    "UPDATE_CONFIG_GENERATOR_DB",
    "UPDATE_CONVEYOR_DASHBOARD_CONVEYORS_CACHE",
    "UPDATE_CONVEYOR_DASHBOARD_FORMULA_COMMIT_TREES_CACHE",
    "UPDATE_CONVEYOR_DASHBOARD_NIRVANA_API_CACHE",
    "UPDATE_CONVEYOR_DASHBOARD_OUTPUT_FORMULA_CACHE",
    "UPDATE_EXTERNAL_DATA",
    "UPDATE_GEOMETASEARCH_ENVIRONMENT",
    "UPDATE_HOSTS_DATA",
    "UPDATE_MAIN_RUBRICS",
    "UPDATE_MAPS_DATABASE_ADVERT",
    "UPDATE_MAPS_DATABASE_POI",
    "UPDATE_MAPS_GEO_HOST_FACTORS",
    "UPDATE_MAPS_GEO_STATIC_FACTORS",
    "UPDATE_MAPS_SEARCH_INDEX",
    "UPDATE_MAPS_STATIC_FACTORS_DOWNLOADER",
    "UPDATE_MAPS_WEB_INDEXANN",
    "UPDATE_MAPS_WIZARD_PPO_DATA",
    "UPDATE_MONGO_STATISTICS",
    "UPDATE_REGULAR_COORDINATES",
    "UPDATE_SIMILAR_ORGS",
    "UPDATE_SIMILAR_ORGS_HYPOTHESES",
    "UPDATE_SVN_RESOUCES_FOR_GEO_TESTS",
    "UPDATE_TESTENV_NEWSD_RESOURCES",
    "UPLOAD_GEOSEARCH_ENTITIES",
    "UPLOAD_IMAGES_DATABASE",
    "UPLOAD_IMAGES_DATABASE_NG",
    "UPLOAD_POETRYLOVER_SHARDMAP",
    "UPLOAD_SMISEARCH_SHARD",
    "UPLOAD_VIDEO_DATABASE",
    "UPLOAD_VIDEO_DATABASE_EXPERIMENTAL_NG",
    "UPLOAD_VIDEO_DATABASE_NG",
    "URLS_BY_SHOW_COUNTERS",
    "USERDATA_PREP_FAST_RUN",
    "USERDATA_PREP_SINGLE_RUN",
    "USER_BROWSE_UPDATE_DATA",
    "USER_BROWSE_UPDATE_FAST_DATA",
    "USER_COUNTERS_UPDATE_DATA",
    "USER_SEARCH_UPDATE_DATA",
    "USER_SEARCH_UPDATE_FAST_DATA",
    "VALIDATE_MATRIXNET_MODELS",
    "VERTICALS_TEST_WRAPPER_2_SIMPLIFIED",
    "VIDEO_ANALYZE_BASESEARCH_CGI_PARAMS",
    "VIDEO_ANALYZE_BASESEARCH_PERFORMANCE",
    "VIDEO_BUILD_AND_TEST_DYNAMIC_MODELS",
    "VIDEO_BUILD_AND_TEST_MIDDLE_DYNAMIC_MODELS",
    "VIDEO_BUILD_BAN_UTILS",
    "VIDEO_BUILD_CONNECTORS_RAW",
    "VIDEO_BUILD_DEEP_CLICK_UTILS",
    "VIDEO_BUILD_DYNAMIC_MODELS",
    "VIDEO_BUILD_MIDDLE_DYNAMIC_MODELS",
    "VIDEO_BUILD_NAILDAEMON",
    "VIDEO_BUILD_PUMPKIN_INDEX",
    "VIDEO_BUILD_PUMPKIN_SERP",
    "VIDEO_BUILD_RKN_BAN",
    "VIDEO_BUILD_UNBAN_RAW",
    "VIDEO_BUILD_VEGAS_CONFIG",
    "VIDEO_COMPARE_DYNAMIC_MODELS",
    "VIDEO_FRESH_RELEASE_QUERYMARKS_TRIE",
    "VIDEO_GET_IDX_OPS_RESPONSES",
    "VIDEO_GET_MIDDLESEARCH_RESPONSES",
    "VIDEO_GET_MIDDLESEARCH_TENV_CACHEHIT",
    "VIDEO_INDEX_VALIDATION",
    "VIDEO_LOAD_BASESEARCH_DATABASE",
    "VIDEO_LOAD_BASESEARCH_TESTENV_DATA",
    "VIDEO_METRICS_INDEX_STABILITY",
    "VIDEO_METRICS_SHARD_SIZE",
    "VIDEO_METRICS_STABILITY",
    "VIDEO_METRICS_STABILITY_HISTORY",
    "VIDEO_METRICS_SWITCH_TIME",
    "VIDEO_METRICS_SWITCH_TIME_HISTORY",
    "VIDEO_METRICS_ULTRA_RECRAWL_DEPTH",
    "VIDEO_METRICS_UPLOAD_STAT",
    "VIDEO_NAILDAEMON_CONFIG",
    "VIDEO_PRIEMKA_BASESEARCH_DATABASE2",
    "VIDEO_RELEASE_BASESEARCH_MODELS",
    "VIDEO_RELEASE_CONTENT_ATTRS",
    "VIDEO_RELEASE_FASTDELIVERY_TRIE",
    "VIDEO_RELEASE_MIDDLESEARCH_MODELS",
    "VIDEO_RELEASE_VIDEOBAN",
    "VIDEO_RELEASE_VIDEOBAN_HASHES",
    "VIDEO_SET_MEDIA_ZK_FLAGS",
    "VIDEO_SHARDMAP_BASE_ULTRA_BY_SVN",
    "VIDEO_SHARDMAP_THUMB_ULTRA_BY_SVN",
    "VIDEO_STORE_SHARDMAP",
    "VIDEO_STORE_SHARDMAP_EXPERIMENTAL",
    "VIDEO_STORE_THUMBS_SHARDMAP",
    "VIDEO_TEST_BASESEARCH_PERFORMANCE",
    "VIDEO_TEST_BASESEARCH_PERFORMANCE_BEST",
    "VIDEO_TEST_BASESEARCH_PERFORMANCE_SSD",
    "VIDEO_TEST_DYNAMIC_MODELS_ARCHIVE",
    "VIDEO_TEST_MIDDLESEARCH_CACHE_RELOAD",
    "VIDEO_TEST_MIDDLESEARCH_MASSIF",
    "VIDEO_TEST_MIDDLESEARCH_MEMCHECK",
    "VIDEO_TEST_MIDDLESEARCH_PERFORMANCE",
    "VIDEO_TEST_MIDDLE_DYNAMIC_MODELS_ARCHIVE",
    "VIDEO_TEST_PUMPKIN_SERP",
    "VPS_BUILD",
    "VPS_BUILD_CI",
    "VPS_CACHE_BUILD",
    "VPS_CUSTOM_CONFIG",
    "VPS_GENERATE_AMMO",
    "WAIT_UPLOAD_IMAGES_DATABASE",
    "WAIT_UPLOAD_VIDEO_DATABASE",
    "WAIT_UPLOAD_VIDEO_DATABASE_EXPERIMENTAL",
    "WATCH_SERP_ITS_FLAGS",
    "WEB_QUERIES_FILTER",
    "WEB_RESULT_SCHEMA_CHECKER",
    "WEB_RESULT_SCHEMA_CHECKER_BASE",
    "WEB_RESULT_SCHEMA_GENERATOR",
    "WIZARD_BETA",
    "WIZARD_LOGS",
    "WIZARD_PROXY_ANSWERS_REQRES",
    "WIZARD_PROXY_COMPARE_REQRES",
    "WIZARD_PROXY_GENERATE_REQRES",
    "WIZARD_QUERIES_PROD",
    "WIZARD_RESPONSES",
    "WIZARD_RUNTIME_BUILD",
    "WIZARD_RUNTIME_BUILD_PATCHED",
    "WIZARD_TEST_PERFORMANCE",
    "WOODY_IMAGE_TEST",
    "YABS_BSCOUNT_PERFORMANCE",
    "YABS_BSCOUNT_PERFORMANCE_BEST",
    "YABS_BSCOUNT_PERFORMANCE_BEST_CMP",
    "YABS_BSCOUNT_PREPARE_UDP_AMMO",
    "YABS_COLLECTORS_MON",
    "YABS_DATA_PREPARE_BRANDS",
    "YABS_DEBUILDER",
    "YABS_DEBUILDER_DEV",
    "YABS_DELAY_SBYT_STAT",
    "YABS_DOWNLOAD_AB_INFO",
    "YABS_DOWNLOAD_HOST_OPTIONS",
    "YABS_DOWNLOAD_SHARDED_TIMESTATS4",
    "YABS_DOWNLOAD_TIMESTATS4",
    "YABS_DUTY_SCHEDULER",
    "YABS_DUTY_SCHEDULE_GENERATOR",
    "YABS_LBYT_JOBS_MONITORING",
    "YABS_LBYT_READER",
    "YABS_LBYT_TASK_MANAGER",
    "YABS_LOGBROKER_AUDIT",
    "YABS_NAV_REG_QUERIES_AGGREGATOR",
    "YABS_REPORT_FOR_SSP",
    "YABS_SERVER_ARCHIVE_CS_INPUT",
    "YABS_SERVER_B2B_PREPARE_SQL",
    "YABS_SERVER_DB_SIZE_AGGREGATE",
    "YABS_SERVER_DB_SIZE_CMP",
    "YABS_SERVER_GET_SQL_ARCHIVE",
    "YABS_SERVER_RUN_CAPACITY_ESTIMATE",
    "YABS_SERVER_SETUP_YA_MAKE",
    "YABS_SERVER_STAT_PERFORMANCE",
    "YABS_SERVER_STAT_PERFORMANCE_BEST",
    "YABS_SERVER_TOOL_ANTISPAM_TASK",
    "YABS_SERVER_TOOL_RTBSHADOW_STAT_TASK",
    "YABS_SERVER_TOOL_SHOW_PROBABILITY_ARBITER_TASK",
    "YABS_WHITE_USERS_TRANSFER",
    "YABS_YQL_CRON_TASKS",
    "YABS_YQL_CRON_TNS_TASK",
    "YABS_YTSTAT_TABLE_CLONER",
    "YABS_YT_BACKUP_RESTORE_19",
    "YABS_YT_STAT_COLLECTOR",
    "YABS_YT_STAT_COORDINATOR",
    "YA_PACKAGE_ACCEPTANCE",
    "YA_TEST_DESCRIPTION_UPDATER",
    "YA_TEST_PARENT",
    "YNDEXER",
    "YOBJECT_BINARY_BUILD",
    "YOBJECT_DATA_BUILD",
    "YT_BACKUP",
}
