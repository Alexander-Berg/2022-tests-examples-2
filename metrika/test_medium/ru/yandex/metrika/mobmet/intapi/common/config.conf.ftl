<?xml version="1.0" encoding="UTF-8"?>
<yandex>

    <settings>
        <daemonRoot>${DAEMON_ROOT}</daemonRoot>
    </settings>

    <mysql_mobile_ro>
        <host>${RECIPE_MYSQL_HOST}</host>
        <port>${RECIPE_MYSQL_PORT}</port>
        <user>${RECIPE_MYSQL_USER}</user>
        <db>mobile</db>
    </mysql_mobile_ro>

    <mysql_mobile_rw>
        <host>${RECIPE_MYSQL_HOST}</host>
        <port>${RECIPE_MYSQL_PORT}</port>
        <user>${RECIPE_MYSQL_USER}</user>
        <db>mobile</db>
    </mysql_mobile_rw>

    <mysql_misc_mobile>
        <host>${RECIPE_MYSQL_HOST}</host>
        <port>${RECIPE_MYSQL_PORT}</port>
        <user>${RECIPE_MYSQL_USER}</user>
        <db>mobile</db>
    </mysql_misc_mobile>

    <mysql_mobile_rbac_ro>
        <host>${RECIPE_MYSQL_HOST}</host>
        <port>${RECIPE_MYSQL_PORT}</port>
        <user>${RECIPE_MYSQL_USER}</user>
        <db>rbac</db>
    </mysql_mobile_rbac_ro>

    <mysql_mobile_rbac_rw>
        <host>${RECIPE_MYSQL_HOST}</host>
        <port>${RECIPE_MYSQL_PORT}</port>
        <user>${RECIPE_MYSQL_USER}</user>
        <db>rbac</db>
    </mysql_mobile_rbac_rw>

    <mysql_counters>
        <host>${RECIPE_MYSQL_HOST}</host>
        <port>${RECIPE_MYSQL_PORT}</port>
        <user>${RECIPE_MYSQL_USER}</user>
        <db>conv_main</db>
    </mysql_counters>

    <mtMobGigaShardedRouterConfig>
        <element index="0">
            <shard>1</shard>
            <replica>
                <host>${RECIPE_CLICKHOUSE_HOST}</host>
                <port>${RECIPE_CLICKHOUSE_HTTP_PORT}</port>
                <datacenter>sas</datacenter>
            </replica>
        </element>
    </mtMobGigaShardedRouterConfig>

    <chTemplateSrcConnectionProperties>
        <user>${RECIPE_CLICKHOUSE_USER}</user>
        <password>${RECIPE_CLICKHOUSE_PASSWORD}</password>
    </chTemplateSrcConnectionProperties>

    <statLogHosts>
        <sources index="0">
            <host>${RECIPE_CLICKHOUSE_HOST}</host>
            <port>${RECIPE_CLICKHOUSE_HTTP_PORT}</port>
            <db>stats</db>
        </sources>
    </statLogHosts>

    <mobileCrashesPgProps>
        <host index="0">${POSTGRES_RECIPE_HOST}</host>
        <port>${POSTGRES_RECIPE_PORT}</port>
        <user>${POSTGRES_RECIPE_USER}</user>
        <db>${POSTGRES_RECIPE_DBNAME}</db>
        <pool>true</pool>
    </mobileCrashesPgProps>

    <ydbMobmetCrashesProperties>
        <endpoint>${YDB_ENDPOINT}</endpoint>
        <database>${YDB_DATABASE}</database>
    </ydbMobmetCrashesProperties>

    <jmxServerConnector>
        <serviceUrl>service:jmx:jmxmp://localhost:${jmxPort}</serviceUrl>
    </jmxServerConnector>

    <tvmSettings>
        <selfClientId>${TVM_SELF_CLIENT_ID}</selfClientId>
        <secret>${TVM_SELF_SECRET}</secret>
        <apiRoot>http://localhost:${TVM_API_PORT}</apiRoot>
    </tvmSettings>

    <requestStatInserter>
        <enabled>false</enabled>
    </requestStatInserter>
</yandex>
