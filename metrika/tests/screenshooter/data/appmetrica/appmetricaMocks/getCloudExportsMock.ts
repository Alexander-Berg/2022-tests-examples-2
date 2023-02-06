import {Mock} from "../../../lib";

export const getCloudExportsResponse =
    {
        "response": [
            {
                "status": 200,
                "data": {
                    "exports": [
                        {
                            "id": 269,
                            "service_account_id": "ajeoruj1mnl39ad3pp12",
                            "cluster_id": "c9q8i65lun4gqf4tavt7",
                            "cluster_name": "magnit",
                            "meta_table_name": "installations",
                            "fields": [
                                "app_version_name",
                                "app_package_name",
                                "install_ipv6",
                                "ios_ifv",
                                "device_type",
                                "connection_type",
                                "install_datetime",
                                "appmetrica_device_id",
                                "tracking_id",
                                "mnc",
                                "city",
                                "install_date",
                                "click_datetime",
                                "click_url_parameters",
                                "install_timestamp",
                                "device_model",
                                "click_timestamp",
                                "match_type",
                                "tracker_name",
                                "is_reinstallation",
                                "publisher_name",
                                "publisher_id",
                                "is_reattribution",
                                "google_aid",
                                "install_receive_datetime",
                                "os_version",
                                "click_ipv6",
                                "install_receive_timestamp",
                                "click_user_agent",
                                "ios_ifa",
                                "device_locale",
                                "application_id",
                                "os_name",
                                "device_manufacturer",
                                "android_id",
                                "country_iso_code",
                                "operator_name",
                                "mcc",
                                "click_id"
                            ],
                            "clickhouse_table_name": "loyalty_installs",
                            "type": "continuous",
                            "status": "ready_for_export",
                            "from_date": "2021-08-01",
                            "create_time": "2021-09-14 09:42:04",
                            "execution_time": "2022-04-04 14:25:24"
                        },
                        {
                            "id": 268,
                            "service_account_id": "ajeoruj1mnl39ad3pp12",
                            "cluster_id": "c9q8i65lun4gqf4tavt7",
                            "cluster_name": "magnit",
                            "meta_table_name": "sessions_starts",
                            "fields": [
                                "city",
                                "device_type",
                                "device_locale",
                                "os_version",
                                "operator_name",
                                "android_id",
                                "device_model",
                                "ios_ifv",
                                "application_id",
                                "app_version_name",
                                "os_name",
                                "connection_type",
                                "mnc",
                                "appmetrica_device_id",
                                "session_start_receive_timestamp",
                                "app_package_name",
                                "mcc",
                                "session_start_datetime",
                                "device_manufacturer",
                                "session_start_timestamp",
                                "session_start_date",
                                "session_start_receive_datetime",
                                "ios_ifa",
                                "country_iso_code",
                                "google_aid"
                            ],
                            "clickhouse_table_name": "loyalty_sessions_start",
                            "type": "continuous",
                            "status": "stopped",
                            "error_message": "",
                            "from_date": "2021-08-01",
                            "create_time": "2021-09-13 19:26:18",
                            "execution_time": "2022-04-01 22:01:17"
                        },
                        {
                            "id": 267,
                            "service_account_id": "ajeoruj1mnl39ad3pp12",
                            "cluster_id": "c9q8i65lun4gqf4tavt7",
                            "cluster_name": "magnit",
                            "meta_table_name": "client_events",
                            "fields": [
                                "event_date",
                                "device_model",
                                "device_locale",
                                "device_type",
                                "event_receive_datetime",
                                "mnc",
                                "event_receive_timestamp",
                                "country_iso_code",
                                "operator_name",
                                "appmetrica_device_id",
                                "app_package_name",
                                "google_aid",
                                "app_version_name",
                                "connection_type",
                                "ios_ifa",
                                "os_version",
                                "city",
                                "device_manufacturer",
                                "event_json",
                                "application_id",
                                "event_name",
                                "mcc",
                                "os_name",
                                "event_timestamp",
                                "ios_ifv",
                                "android_id",
                                "event_datetime"
                            ],
                            "clickhouse_table_name": "loyalty_events",
                            "type": "continuous",
                            "status": "ready_for_export",
                            "error_message": "",
                            "from_date": "2020-08-01",
                            "create_time": "2021-09-13 19:25:42",
                            "execution_time": "2022-04-04 13:40:27"
                        },
                    ],
                    "totals": 3,
                    "_profile": {
                        "queries": [
                            {
                                "host": "mdbliv24jkovhf87tjs0.haproxy-prod.metrika.yandex.net:3306",
                                "database": "mobile",
                                "query": "SELECT COUNT(*) FROM applications WHERE id IN (2814495) AND `status` <> 'deleted'",
                                "time": 1,
                                "rows": 0,
                                "request_id": "1649073448145932-1761596681047990435",
                                "event_date_time": "2022-04-04 14:57:28",
                                "daemon_name": "yandex-metrika-mobmetd",
                                "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                "db_type": "mysql",
                                "base_time": 1649073448153,
                                "query_hash": 975835054
                            },
                            {
                                "database": "ru.yandex.metrika.dbclients.routing.TransactionDefinitionRoutingDataSource@782b12c9",
                                "query": "SELECT    id,   uuid,   application_id,   service_account_id,   cluster_id,   meta_table_name,   fields,   clickhouse_table_name,   table_type,   type,   status,   error_message,   from_date,   to_date,   create_time,   execution_time  FROM cloud.export WHERE application_id = ? AND   type = CAST(? AS cloud.export_type)",
                                "params": "[2814495, continuous]",
                                "time": 4,
                                "rows": 8,
                                "request_id": "1649073448145932-1761596681047990435",
                                "event_date_time": "2022-04-04 14:57:28",
                                "daemon_name": "yandex-metrika-mobmetd",
                                "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                "db_type": "postgres",
                                "base_time": 1649073448155,
                                "query_hash": 1379415954
                            }
                        ],
                        "additional": {
                            "frontend-host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net:8080"
                        },
                        "base_time": 1649073448152,
                        "request_id": "1649073448145932-1761596681047990435",
                        "request_uid": 1406498655,
                        "total_time": 8,
                        "java_time": 3
                    }
                },
                "_profile": [
                    {
                        "type": "api-request",
                        "data": {
                            "baseTime": 1649073448116,
                            "success": true,
                            "url": "http://localhost:4/tvm/tickets?dsts=2000337%2C222%2C2000268",
                            "method": "get",
                            "time": 8,
                            "headers": null,
                            "data": "null",
                            "error": false
                        },
                        "isBlackbox": false
                    },
                    {
                        "type": "api-request",
                        "data": {
                            "baseTime": 1649073448114,
                            "success": true,
                            "url": "http://blackbox.yandex.net/blackbox?method=sessionid&host=appmetrica.yandex.ru&userip=2a02%3A6b8%3A81%3A0%3A102c%3A5203%3A5f0a%3Ae24f&regname=yes&format=json&emails=getdefault&dbfields=subscription.login.669&get_user_ticket=1",
                            "method": "get",
                            "time": 16,
                            "headers": null,
                            "data": "null",
                            "error": false
                        },
                        "isBlackbox": true
                    },
                    {
                        "type": "api-request",
                        "data": {
                            "baseTime": 1649073448133,
                            "success": true,
                            "url": "http://blackbox.yandex.net/blackbox?method=checkip&ip=2a02%3A6b8%3A81%3A0%3A102c%3A5203%3A5f0a%3Ae24f&nets=yandexusers&format=json",
                            "method": "get",
                            "time": 4,
                            "headers": null,
                            "data": "null",
                            "error": false
                        },
                        "isBlackbox": true
                    },
                    {
                        "type": "api-request",
                        "data": {
                            "baseTime": 1649073448138,
                            "success": true,
                            "url": "http://uatraits.qloud.yandex.ru/v0/detect",
                            "method": "POST",
                            "time": 4,
                            "headers": null,
                            "post": "{\n  \"User-Agent\": \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15\"\n}",
                            "data": "{\n  \"isTouch\": false,\n  \"isMobile\": false,\n  \"isBrowser\": true,\n  \"OSVersion\": \"10.15.7\",\n  \"OSName\": \"macOS Catalina\",\n  \"AntiITP\": true,\n  \"ITP\": true,\n  \"OSFamily\": \"MacOS\",\n  \"BrowserVersion\": \"15.2\",\n  \"BrowserEngineVersion\": \"605.1.15\",\n  \"BrowserName\": \"Safari\",\n  \"CSP1Support\": true,\n  \"CSP2Support\": true,\n  \"BrowserEngine\": \"WebKit\",\n  \"ITPFakeCookie\": true\n}",
                            "error": false
                        },
                        "isBlackbox": false
                    },
                    {
                        "type": "api-request",
                        "data": {
                            "baseTime": 1649073448145,
                            "success": true,
                            "url": "http://mobmetd-production.metrika.yandex.net/management/v1/application/2814495/export/cloud?interface=1&lang=ru&request_domain=ru&sort=create_time&limit=10&offset=0&sort_order=desc&export_type=CONTINUOUS&uid=1406498655",
                            "method": "get",
                            "time": 17,
                            "headers": null,
                            "data": "{\n  \"exports\": [\n    {\n      \"id\": 269,\n      \"service_account_id\": \"ajeoruj1mnl39ad3pp12\",\n      \"cluster_id\": \"c9q8i65lun4gqf4tavt7\",\n      \"cluster_name\": \"magnit\",\n      \"meta_table_name\": \"installations\",\n      \"fields\": [\n        \"app_version_name\",\n        \"app_package_name\",\n        \"install_ipv6\",\n        \"ios_ifv\",\n        \"device_type\",\n        \"connection_type\",\n        \"install_datetime\",\n        \"appmetrica_device_id\",\n        \"tracking_id\",\n        \"mnc\",\n        \"city\",\n        \"install_date\",\n        \"click_datetime\",\n        \"click_url_parameters\",\n        \"install_timestamp\",\n        \"device_model\",\n        \"click_timestamp\",\n        \"match_type\",\n        \"tracker_name\",\n        \"is_reinstallation\",\n        \"publisher_name\",\n        \"publisher_id\",\n        \"is_reattribution\",\n        \"google_aid\",\n        \"install_receive_datetime\",\n        \"os_version\",\n        \"click_ipv6\",\n        \"install_receive_timestamp\",\n        \"click_user_agent\",\n        \"ios_ifa\",\n        \"device_locale\",\n        \"application_id\",\n        \"os_name\",\n        \"device_manufacturer\",\n        \"android_id\",\n        \"country_iso_code\",\n        \"operator_name\",\n        \"mcc\",\n        \"click_id\"\n      ],\n      \"clickhouse_table_name\": \"loyalty_installs\",\n      \"type\": \"continuous\",\n      \"status\": \"ready_for_export\",\n      \"from_date\": \"2021-08-01\",\n      \"create_time\": \"2021-09-14 09:42:04\",\n      \"execution_time\": \"2022-04-04 14:25:24\"\n    },\n    {\n      \"id\": 268,\n      \"service_account_id\": \"ajeoruj1mnl39ad3pp12\",\n      \"cluster_id\": \"c9q8i65lun4gqf4tavt7\",\n      \"cluster_name\": \"magnit\",\n      \"meta_table_name\": \"sessions_starts\",\n      \"fields\": [\n        \"city\",\n        \"device_type\",\n        \"device_locale\",\n        \"os_version\",\n        \"operator_name\",\n        \"android_id\",\n        \"device_model\",\n        \"ios_ifv\",\n        \"application_id\",\n        \"app_version_name\",\n        \"os_name\",\n        \"connection_type\",\n        \"mnc\",\n        \"appmetrica_device_id\",\n        \"session_start_receive_timestamp\",\n        \"app_package_name\",\n        \"mcc\",\n        \"session_start_datetime\",\n        \"device_manufacturer\",\n        \"session_start_timestamp\",\n        \"session_start_date\",\n        \"session_start_receive_datetime\",\n        \"ios_ifa\",\n        \"country_iso_code\",\n        \"google_aid\"\n      ],\n      \"clickhouse_table_name\": \"loyalty_sessions_start\",\n      \"type\": \"continuous\",\n      \"status\": \"stopped\",\n      \"error_message\": \"\",\n      \"from_date\": \"2021-08-01\",\n      \"create_time\": \"2021-09-13 19:26:18\",\n      \"execution_time\": \"2022-04-01 22:01:17\"\n    },\n    {\n      \"id\": 267,\n      \"service_account_id\": \"ajeoruj1mnl39ad3pp12\",\n      \"cluster_id\": \"c9q8i65lun4gqf4tavt7\",\n      \"cluster_name\": \"magnit\",\n      \"meta_table_name\": \"client_events\",\n      \"fields\": [\n        \"event_date\",\n        \"device_model\",\n        \"device_locale\",\n        \"device_type\",\n        \"event_receive_datetime\",\n        \"mnc\",\n        \"event_receive_timestamp\",\n        \"country_iso_code\",\n        \"operator_name\",\n        \"appmetrica_device_id\",\n        \"app_package_name\",\n        \"google_aid\",\n        \"app_version_name\",\n        \"connection_type\",\n        \"ios_ifa\",\n        \"os_version\",\n        \"city\",\n        \"device_manufacturer\",\n        \"event_json\",\n        \"application_id\",\n        \"event_name\",\n        \"mcc\",\n        \"os_name\",\n        \"event_timestamp\",\n        \"ios_ifv\",\n        \"android_id\",\n        \"event_datetime\"\n      ],\n      \"clickhouse_table_name\": \"loyalty_events\",\n      \"type\": \"continuous\",\n      \"status\": \"ready_for_export\",\n      \"error_message\": \"\",\n      \"from_date\": \"2020-08-01\",\n      \"create_time\": \"2021-09-13 19:25:42\",\n      \"execution_time\": \"2022-04-04 13:40:27\"\n    },\n    {\n      \"id\": 201,\n      \"service_account_id\": \"ajeoruj1mnl39ad3pp12\",\n      \"cluster_id\": \"c9q8i65lun4gqf4tavt7\",\n      \"cluster_name\": \"magnit\",\n      \"meta_table_name\": \"sessions_starts\",\n      \"fields\": [\n        \"city\",\n        \"device_type\",\n        \"device_locale\",\n        \"os_version\",\n        \"operator_name\",\n        \"android_id\",\n        \"device_model\",\n        \"ios_ifv\",\n        \"application_id\",\n        \"app_version_name\",\n        \"os_name\",\n        \"connection_type\",\n        \"mnc\",\n        \"appmetrica_device_id\",\n        \"session_start_receive_timestamp\",\n        \"app_package_name\",\n        \"mcc\",\n        \"session_start_datetime\",\n        \"device_manufacturer\",\n        \"session_start_timestamp\",\n        \"session_start_date\",\n        \"session_start_receive_datetime\",\n        \"ios_ifa\",\n        \"country_iso_code\",\n        \"google_aid\"\n      ],\n      \"clickhouse_table_name\": \"loyalty_sessions_start\",\n      \"type\": \"continuous\",\n      \"status\": \"stopped\",\n      \"error_message\": \"\",\n      \"from_date\": \"2019-07-04\",\n      \"create_time\": \"2021-08-05 14:29:37\",\n      \"execution_time\": \"2021-09-13 16:17:05\"\n    },\n    {\n      \"id\": 200,\n      \"service_account_id\": \"ajeoruj1mnl39ad3pp12\",\n      \"cluster_id\": \"c9q8i65lun4gqf4tavt7\",\n      \"cluster_name\": \"magnit\",\n      \"meta_table_name\": \"installations\",\n      \"fields\": [\n        \"app_version_name\",\n        \"app_package_name\",\n        \"install_ipv6\",\n        \"ios_ifv\",\n        \"device_type\",\n        \"connection_type\",\n        \"install_datetime\",\n        \"appmetrica_device_id\",\n        \"tracking_id\",\n        \"mnc\",\n        \"city\",\n        \"install_date\",\n        \"click_datetime\",\n        \"click_url_parameters\",\n        \"install_timestamp\",\n        \"device_model\",\n        \"click_timestamp\",\n        \"match_type\",\n        \"tracker_name\",\n        \"is_reinstallation\",\n        \"publisher_name\",\n        \"publisher_id\",\n        \"is_reattribution\",\n        \"google_aid\",\n        \"install_receive_datetime\",\n        \"os_version\",\n        \"click_ipv6\",\n        \"install_receive_timestamp\",\n        \"click_user_agent\",\n        \"ios_ifa\",\n        \"device_locale\",\n        \"application_id\",\n        \"os_name\",\n        \"device_manufacturer\",\n        \"android_id\",\n        \"country_iso_code\",\n        \"operator_name\",\n        \"mcc\",\n        \"click_id\"\n      ],\n      \"clickhouse_table_name\": \"loyalty_installs\",\n      \"type\": \"continuous\",\n      \"status\": \"stopped\",\n      \"error_message\": \"\",\n      \"from_date\": \"2019-07-04\",\n      \"create_time\": \"2021-08-05 14:27:52\",\n      \"execution_time\": \"2021-09-13 16:20:04\"\n    },\n    {\n      \"id\": 199,\n      \"service_account_id\": \"ajeoruj1mnl39ad3pp12\",\n      \"cluster_id\": \"c9q8i65lun4gqf4tavt7\",\n      \"cluster_name\": \"magnit\",\n      \"meta_table_name\": \"client_events\",\n      \"fields\": [\n        \"event_date\",\n        \"device_model\",\n        \"device_locale\",\n        \"device_type\",\n        \"event_receive_datetime\",\n        \"mnc\",\n        \"event_receive_timestamp\",\n        \"country_iso_code\",\n        \"operator_name\",\n        \"appmetrica_device_id\",\n        \"app_package_name\",\n        \"google_aid\",\n        \"app_version_name\",\n        \"connection_type\",\n        \"ios_ifa\",\n        \"os_version\",\n        \"city\",\n        \"device_manufacturer\",\n        \"event_json\",\n        \"application_id\",\n        \"os_name\",\n        \"mcc\",\n        \"event_name\",\n        \"event_timestamp\",\n        \"ios_ifv\",\n        \"android_id\",\n        \"event_datetime\"\n      ],\n      \"clickhouse_table_name\": \"loyalty_events\",\n      \"type\": \"continuous\",\n      \"status\": \"stopped\",\n      \"error_message\": \"\",\n      \"from_date\": \"2019-07-04\",\n      \"create_time\": \"2021-08-05 14:27:28\",\n      \"execution_time\": \"2021-09-13 16:18:50\"\n    },\n    {\n      \"id\": 198,\n      \"service_account_id\": \"ajeoruj1mnl39ad3pp12\",\n      \"cluster_id\": \"c9q8i65lun4gqf4tavt7\",\n      \"cluster_name\": \"magnit\",\n      \"meta_table_name\": \"client_events\",\n      \"fields\": [\n        \"event_date\",\n        \"device_model\",\n        \"device_locale\",\n        \"device_type\",\n        \"event_receive_datetime\",\n        \"mnc\",\n        \"event_receive_timestamp\",\n        \"country_iso_code\",\n        \"operator_name\",\n        \"appmetrica_device_id\",\n        \"app_package_name\",\n        \"google_aid\",\n        \"app_version_name\",\n        \"connection_type\",\n        \"ios_ifa\",\n        \"os_version\",\n        \"city\",\n        \"device_manufacturer\",\n        \"event_json\",\n        \"application_id\",\n        \"os_name\",\n        \"mcc\",\n        \"event_name\",\n        \"event_timestamp\",\n        \"ios_ifv\",\n        \"android_id\",\n        \"event_datetime\"\n      ],\n      \"clickhouse_table_name\": \"loyalty_appmetrica_events\",\n      \"type\": \"continuous\",\n      \"status\": \"stopped\",\n      \"from_date\": \"2019-07-04\",\n      \"create_time\": \"2021-08-05 14:19:18\"\n    },\n    {\n      \"id\": 196,\n      \"service_account_id\": \"ajeoruj1mnl39ad3pp12\",\n      \"cluster_id\": \"c9q8i65lun4gqf4tavt7\",\n      \"cluster_name\": \"magnit\",\n      \"meta_table_name\": \"installations\",\n      \"fields\": [\n        \"app_version_name\",\n        \"app_package_name\",\n        \"install_ipv6\",\n        \"ios_ifv\",\n        \"device_type\",\n        \"connection_type\",\n        \"install_datetime\",\n        \"appmetrica_device_id\",\n        \"tracking_id\",\n        \"mnc\",\n        \"city\",\n        \"install_date\",\n        \"click_datetime\",\n        \"click_url_parameters\",\n        \"install_timestamp\",\n        \"device_model\",\n        \"click_timestamp\",\n        \"match_type\",\n        \"tracker_name\",\n        \"is_reinstallation\",\n        \"publisher_name\",\n        \"publisher_id\",\n        \"is_reattribution\",\n        \"google_aid\",\n        \"install_receive_datetime\",\n        \"os_version\",\n        \"click_ipv6\",\n        \"install_receive_timestamp\",\n        \"click_user_agent\",\n        \"ios_ifa\",\n        \"device_locale\",\n        \"application_id\",\n        \"os_name\",\n        \"device_manufacturer\",\n        \"android_id\",\n        \"country_iso_code\",\n        \"operator_name\",\n        \"mcc\",\n        \"click_id\"\n      ],\n      \"clickhouse_table_name\": \"loyalty_appmetrica_installs\",\n      \"type\": \"continuous\",\n      \"status\": \"stopped\",\n      \"from_date\": \"2019-07-04\",\n      \"create_time\": \"2021-08-05 12:37:17\",\n      \"execution_time\": \"2021-08-05 14:22:01\"\n    }\n  ],\n  \"totals\": 8\n}",
                            "error": false,
                            "_profile": {
                                "queries": [
                                    {
                                        "host": "mdbliv24jkovhf87tjs0.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "mobile",
                                        "query": "SELECT COUNT(*) FROM applications WHERE id IN (2814495) AND `status` <> 'deleted'",
                                        "time": 1,
                                        "rows": 0,
                                        "request_id": "1649073448145932-1761596681047990435",
                                        "event_date_time": "2022-04-04 14:57:28",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1649073448153,
                                        "query_hash": 975835054
                                    },
                                    {
                                        "database": "ru.yandex.metrika.dbclients.routing.TransactionDefinitionRoutingDataSource@782b12c9",
                                        "query": "SELECT    id,   uuid,   application_id,   service_account_id,   cluster_id,   meta_table_name,   fields,   clickhouse_table_name,   table_type,   type,   status,   error_message,   from_date,   to_date,   create_time,   execution_time  FROM cloud.export WHERE application_id = ? AND   type = CAST(? AS cloud.export_type)",
                                        "params": "[2814495, continuous]",
                                        "time": 4,
                                        "rows": 8,
                                        "request_id": "1649073448145932-1761596681047990435",
                                        "event_date_time": "2022-04-04 14:57:28",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "postgres",
                                        "base_time": 1649073448155,
                                        "query_hash": 1379415954
                                    }
                                ],
                                "additional": {
                                    "frontend-host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net:8080"
                                },
                                "base_time": 1649073448152,
                                "request_id": "1649073448145932-1761596681047990435",
                                "request_uid": 1406498655,
                                "total_time": 8,
                                "java_time": 3
                            }
                        },
                        "isBlackbox": false
                    }
                ],
                "_version": "2.1243321415.2"
            }
        ]
    };

export const getCloudExportsMock = new Mock(
    /.*\/transport\/i-cloud\/getCloudExportsList*/,
    getCloudExportsResponse
);

